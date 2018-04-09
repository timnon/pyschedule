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



def solve(scenario,time_limit=None,copy_scenario=False,msg=0) :
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
		I = ort_solver.FixedDurationIntervalVar(0,S.horizon-T.length,T.length,False,T.name)
		task_to_interval[T] = I




	# resourcee requirements
	for T in S.tasks():
		I = task_to_interval[T]
		for RA in T.resources_req:
			RA_tasks = list()
			for R in RA :
				I_ = ort_solver.FixedDurationIntervalVar(0,S.horizon-T.length,T.length,True,T.name+'_'+R.name)
				resource_to_intervals[R].append(I_)
				RA_tasks.append(I_)
				resource_task_to_interval[(R,T)] = I_
				ort_solver.Add( I.StaysInSync(I_) )
				# if resources are fixed
				if T.resources is not None and R in T.resources :
					ort_solver.Add( I_.PerformedExpr() == 1 )
			# one resource needs to get selected
			ort_solver.Add(ort_solver.Sum([ I_.PerformedExpr() for I_ in RA_tasks ]) == 1)
	ra_to_tasks = S.resources_req_tasks()
	for RA in ra_to_tasks:
		tasks = list(ra_to_tasks[RA])
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
	ort_objective_var = ort_solver.Sum([ task_to_interval[T].EndExpr()*T.completion_time_cost
										 for T in S.tasks() if T in task_to_interval
										 and 'completion_time_cost' in T ])
	ort_objective = ort_solver.Minimize(ort_objective_var, 1)

	# precedences lax
	for P in S.precs_lax() :
		ort_solver.Add( task_to_interval[P.task_right].StartsAfterEnd( task_to_interval[P.task_left] ) )
		# TODO: add offset, but this requires DependecyGraph which is not exposed via swig?

	# precedences tight
	for P in S.precs_tight() :
		ort_solver.Add( task_to_interval[P.task_right].StartsAtEnd( task_to_interval[P.task_left] ) )
		# TODO: add offset, but this requires DependecyGraph which is not exposed via swig?

	# bound low
	for P in S.bounds_low() :
		ort_solver.Add( task_to_interval[P.task].StartsAfter(P.bound) )

	# bound up
	for P in S.bounds_up() :
		ort_solver.Add( task_to_interval[P.task].StartsBefore(P.bound) )

	# tight bound low
	for P in S.bounds_low_tight() :
		ort_solver.Add( task_to_interval[P.task].StartsAt(P.bound) )

	# tight bound up
	for P in S.bounds_up_tight() :
		ort_solver.Add( task_to_interval[P.task].EndsAt(P.bound) )

	# capacity lower bounds
	for C in S.capacity_low():
		# ignore sliced capacity constraints
		if C._start != None or C._end != None:
			continue
		R = C.resource
		cap_tasks = [ (resource_task_to_interval[R,T],C.weight(T=T,t=0)) for T in S.tasks() ]
		ort_solver.Add( ort_solver.Sum([ I.PerformedExpr()*w for I,w in cap_tasks ]) >= C.bound )

	# capacity lower bounds
	for C in S.capacity_low():
		# ignore sliced capacity constraints
		if C._start != None or C._end != None:
			continue
		R = C.resource
		cap_tasks = [ (resource_task_to_interval[R,T],C.weight(T=T,t=0)) for T in S.tasks() ]
		ort_solver.Add( ort_solver.Sum([ I.PerformedExpr()*w for I,w in cap_tasks ]) <= C.bound )

	# creates search phases.
	vars_phase = ort_solver.Phase([ort_objective_var],
		            ort_solver.CHOOSE_FIRST_UNBOUND,
		            ort_solver.ASSIGN_MIN_VALUE)
	sequence_phase = ort_solver.Phase(list(sequences.values()),
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

	# check for a solution
	if not collector.SolutionCount():
		if msg:
			print('ERROR: no solution found')
		return 0
	solution = collector.Solution(0)

	# read last solution
	for T in S.tasks() :
		T.start_value = int(solution.StartMin(task_to_interval[T])) #collector.StartValue(0, task_to_interval[T])
		T.resources = [ R \
	                    for RA in T.resources_req for R in RA \
	                    if collector.PerformedValue(0,resource_task_to_interval[(R,T)]) == 1 ]
	return 1
	


































