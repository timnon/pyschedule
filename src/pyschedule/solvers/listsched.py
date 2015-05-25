#! /usr/bin/env python
from __future__ import print_function

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

import copy

def sort_with_precs(scenario) :
	"""
	returns the tasks of the given scenario sorted according to the
	lax precedence constraints and next according to the task length,
	where large tasks have priority
	"""
	S = scenario

	'''
	# get direct children for topological sort
	children = { T : set() for T in S.tasks() }
	for P in S.precs_lax() :
		children[P.left].add(P.right)
	# extend children to other descendents
	for T in S.tasks() :
		task_stack = {T}
		while task_stack :
			T_ = task_stack.pop()
			children[T] = children[T] | children[T_]
			task_stack = task_stack | children[T_]
	'''

	import networkx as nx
	G = nx.DiGraph()
	G.add_nodes_from(S.tasks())
	G.add_edges_from([ (P.left,P.right) for P in S.precs_lax() ])
	task_list = nx.algorithms.topological_sort(G)
	return task_list


#TODO: list as parameter of solving procedure
def solve(scenario,solve_method,task_list=None,batch_size=1,copy_scenario=False,msg=0) :
	"""
	Iteratively adds tasks and uses solve_method to integrate these
	tasks into the schedule.

	Arguments:
		scenario   : the scenario to solve
		task_list  : list of all tasks which defines the order in which all tasks are
                             added to the schedule
		batch_size : the number of tasks to integrate in the schedule at a time
	"""

	S = scenario
	if copy_scenario :
		S = copy.deepcopy(scenario)

	if not S.objective :
		S.use_makespan_objective()

	if not task_list :
		task_list = sort_with_precs(S)
		task_list = [ T for T in task_list if T.start is None ]

	constraints = S.constraints # keep references and clear old reference list
	S.constraints = []

	#non_objective_tasks = [ T for T in task_list if not T.objective ]
	for T in task_list : S -= T #remove all tasks which are not part of objective

	def batches(tasks, batch_size):
		for i in xrange(0, len(tasks), batch_size):
			yield tasks[i:i+batch_size]
	
	for batch in batches(task_list,batch_size) :
		if msg :
			print('INFO: batch for list scheduling '+','.join([ str(T) for T in batch]))
		for T in batch :
			S += T
		S.constraints = [ C for C in constraints if set(C.tasks()).issubset(set(S.tasks())) ]
		#S.T['MakeSpan'].start = None #remove objective

		solve_method(S)
		'''
		import pyschedule
		pyschedule.plotters.matplotlib.plot(S)
		'''
		
		


		
		

		

	



