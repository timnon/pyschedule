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
		
	# no objective specified
	if not S.objective :
		S.use_makespan_objective()

	ort_solver = pywrapcp.Solver(S.name)

	# tasks
	task_to_interval = collections.OrderedDict()
	resource_to_intervals = resource_to_intervals = { R : list() for R in S.resources() }
	resource_task_to_interval = collections.OrderedDict()
	for T in S.tasks() :
		I = ort_solver.FixedDurationIntervalVar(0,horizon,T.length,False,T.name)
		task_to_interval[T] = I

		# fix start
		if T.start is not None :
			ort_solver.Add(I.StartsAt(T.start))

		# fix resources 
		if T.resources :
			for R in T.resources :
				resource_to_intervals[R].append(I)
				'''
				I_ = ort_solver.FixedDurationIntervalVar(0,horizon,T.length,True,T.name+'_'+R.name)
				resource_to_intervals[R].append(I_)
				resource_task_to_interval[(R,T)] = I_
				ort_solver.Add( I.StaysInSync(I_) )
				'''
		# alternative resources
		else :
			for RA in T.resources_req :
				ra_tasks = list()
				for R in RA :
					I_ = ort_solver.FixedDurationIntervalVar(0,horizon,T.length,True,T.name+'_'+R.name)
					resource_to_intervals[R].append(I_)
					ra_tasks.append(I_)
					resource_task_to_interval[(R,T)] = I_
					ort_solver.Add( I.StaysInSync(I_) )
				# one resource needs to get selected
	  			ort_solver.Add(ort_solver.Sum([ I_.PerformedExpr() for I_ in ra_tasks ]) == 1)

	# resources
	sequences = collections.OrderedDict()
	for R in S.resources() :
		disj = ort_solver.DisjunctiveConstraint(resource_to_intervals[R],R.name)
		sequences[R] = disj.SequenceVar()
		ort_solver.Add(disj)

	# move objective
	# TODO: bug, variables that are not part of the objective might not be finally defined
	ort_objective_var = ort_solver.Sum([ task_to_interval[T].EndExpr()*1 for T in S.tasks() ]+
                                           [ task_to_interval[T].EndExpr()*1000000 for T in S.objective ])
	ort_objective = ort_solver.Minimize(ort_objective_var, 1)

	# precedences
	for P in S.precs_lax() :
		ort_solver.Add( task_to_interval[P.right].StartsAfterEnd( task_to_interval[P.left] ) )
		# TODO: add offset, but this requires DependecyGraph which is not exposed via swig?

	# precedences low 
	for P in S.precs_low() :
		ort_solver.Add( task_to_interval[P.left].StartsAfter(P.right) )

	# precedences up 
	for P in S.precs_up() :
		ort_solver.Add( task_to_interval[P.left].StartsBefore(P.right) )

	# creates search phases.
	vars_phase = ort_solver.Phase([ort_objective_var],
		            ort_solver.CHOOSE_FIRST_UNBOUND,
		            ort_solver.ASSIGN_MIN_VALUE)
	sequence_phase = ort_solver.Phase([sequences[R] for R in S.resources() ],
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

	# get last solution
	for T in S.tasks() :
		if T.start is None :
			T.start = collector.StartValue(0, task_to_interval[T])
		if not T.resources :
			T.resources = [ R \
		                        for RA in T.resources_req for R in RA \
		                        if collector.PerformedValue(0,resource_task_to_interval[(R,T)]) == 1 ]
	


































