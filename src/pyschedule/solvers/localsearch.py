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

import copy, random

def select_random_tasks(scenario,batch_size=20) :
	"""
	selects some random tasks
	"""
	return random.sample(scenario.tasks(),batch_size)



def solve(scenario,solve_method,select_method=select_random_tasks,n_iterations=10,copy_scenario=False,msg=0) :
	"""
	Iteratively removes and adds tasks

	Arguments:
		scenario: the scenario to solve
		solve_method : the solve method to integrate free tasks
	"""

	S = scenario
	if copy_scenario :
		S = copy.deepcopy(scenario)

	if not S.objective :
		S.use_makespan_objective()

	for i in range(n_iterations) :
		if msg :
			print('INFO: iteration '+str(i))
		opt_tasks = select_method(S)
		for T in opt_tasks :
			T.start = None
			#T.resources = None
		for T in S.objective :
			if T in S.tasks() :
				T.start = None
		solve_method(S)
		
		import pyschedule
		pyschedule.plotters.matplotlib.plot(S)
		
		
		
		


		
		

		

	



