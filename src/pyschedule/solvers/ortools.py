#! /usr/bin/env python
from __future__ import absolute_import as _absolute_import

'''
Copyright 2015 Tim Nonner
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''

import time, os, copy, collections



def solve(scenario,horizon,time_limit=None,copy_scenario=False,msg=0) :
	"""
	Integration of the ortools scheduling solver
	"""

	try :
		from ortools.constraint_solver import pywrapcp
	except :
		raise Exception('ERROR: ortools is not installed')

	S = scenario
	if copy_scenario :
		S = copy.deepcopy(scenario)

	ort_solver = pywrapcp.Solver(S.name)

	# tasks
	task_to_interval = collections.OrderedDict()
	resource_to_intervals = resource_to_intervals = { R : list() for R in S.resources() }
	resource_task_to_interval = collections.OrderedDict()
	for T in S.tasks() :
		I = ort_solver.FixedDurationIntervalVar(0,horizon-T.length,T.length,False,T.name)
		task_to_interval[T] = I

		# fix start
		if T.start is not None :
			ort_solver.Add(I.StartsAt(T.start))

	# resourcee requirements
	for RA in S.resources_req() :
		tasks = RA.tasks()
		for T in tasks :
			I = task_to_interval[T]
			RA_tasks = list()
			for R in RA :
				I_ = ort_solver.FixedDurationIntervalVar(0,horizon-T.length,T.length,True,T.name+'_'+R.name)
				resource_to_intervals[R].append(I_)
				RA_tasks.append(I_)
				resource_task_to_interval[(R,T)] = I_
				ort_solver.Add( I.StaysInSync(I_) )
				# if resources are fixed
				if T.resources is not None and R in T.resources :
					ort_solver.Add( I_.PerformedExpr() == 1 )
			# one resource needs to get selected
			ort_solver.Add(ort_solver.Sum([ I_.PerformedExpr() for I_ in RA_tasks ]) == 1)
		# same resources for tasks
		T = tasks[0]
		for T_ in tasks[1:] :
			for R in RA :
				I  = resource_task_to_interval[(R,T)]
				I_ = resource_task_to_interval[(R,T_)]
				ort_solver.Add( I.PerformedExpr() == I_.PerformedExpr() )

	# resources
	sequences = collections.OrderedDict()
	for R in S.resources() :
		disj = ort_solver.DisjunctiveConstraint(resource_to_intervals[R],R.name)
		sequences[R] = disj.SequenceVar()
		ort_solver.Add(disj)

	# move objective
	# TODO: bug, variables that are not part of the objective might not be finally defined
	ort_objective_var = ort_solver.Sum([ task_to_interval[T].EndExpr()*S.objective[T] for T in S.objective if T in task_to_interval ])#+
                                          #[ task_to_interval[T].EndExpr()*1 for T in S.tasks() ])
	ort_objective = ort_solver.Minimize(ort_objective_var, 1)

	# precedences
	for P in S.precs_lax() :
		ort_solver.Add( task_to_interval[P.right].StartsAfterEnd( task_to_interval[P.left] ) )
		# TODO: add offset, but this requires DependecyGraph which is not exposed via swig?

	# precedences
	for P in S.precs_tight() :
		ort_solver.Add( task_to_interval[P.right].StartsAtEnd( task_to_interval[P.left] ) )
		# TODO: add offset, but this requires DependecyGraph which is not exposed via swig?

	# precedences low 
	for P in S.precs_low() :
		ort_solver.Add( task_to_interval[P.left].StartsAfter(P.right) )

	# precedences up 
	for P in S.precs_up() :
		ort_solver.Add( task_to_interval[P.left].StartsBefore(P.right) )

	'''
	# ensure that tasks with similar precedences are run on the same resources
	same_resource_precs = list()
	if S.is_same_resource_precs_lax :
		same_resource_precs.extend(S.precs_lax())
	if S.is_same_resource_precs_tight :
		same_resource_precs.extend(S.precs_tight())
	for P in same_resource_precs :
		shared_resources = set(P.left.resources_req_list()) & set(P.right.resources_req_list())
		for R in shared_resources :
			I_left = resource_task_to_interval[(R,P.left)]
			I_right = resource_task_to_interval[(R,P.right)]
			ort_solver.Add( I_left.PerformedExpr() == I_right.PerformedExpr() )
	'''

	# creates search phases.
	vars_phase = ort_solver.Phase([ort_objective_var],
		            ort_solver.CHOOSE_FIRST_UNBOUND,
		            ort_solver.ASSIGN_MIN_VALUE)
	sequence_phase = ort_solver.Phase(sequences.values(),
		                ort_solver.SEQUENCE_DEFAULT)
	main_phase = ort_solver.Compose([sequence_phase, vars_phase])

	# creates the search log.
	search_log = ort_solver.SearchLog(100, ort_objective_var)

	# collect solution
	solution = ort_solver.Assignment()
	for T in S.tasks() :
		solution.Add(task_to_interval[T])
	for R in S.resources() :
		for I in resource_to_intervals[R] :
			solution.Add(I)
	collector = ort_solver.LastSolutionCollector(solution)

	# set limits (time limit im ms)
	if time_limit :
		ort_time_limit = int(time_limit*1000)
	else :
		ort_time_limit = 100000000
	branch_limit = 100000000	
	failures_limit = 100000000
	solutions_limit = 10000000
	limits = (ort_solver.Limit(ort_time_limit, branch_limit, failures_limit, solutions_limit, True))

	# add log if mst is requested
	search_params = [limits,collector,ort_objective]
	if msg :
		search_params.append(search_log)

	# solves the problem.
	ort_solver.Solve(main_phase,search_params)

	solution = collector.Solution(0)

	# get last solution
	for T in S.tasks() :
		if T.start is None :
			T.start = int(solution.StartMin(task_to_interval[T])) #collector.StartValue(0, task_to_interval[T])
		if not T.resources :
			RAs = S.resources_req(task=T)
			T.resources = [ R \
		                    for RA in RAs for R in RA \
		                    if collector.PerformedValue(0,resource_task_to_interval[(R,T)]) == 1 ]
	


































