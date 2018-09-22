#! /usr/bin/python
from __future__ import absolute_import as _absolute_import
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

from .mip_pulp import MIP
import collections



def solve(scenario, bigm=10000, kind='CBC', time_limit=None, random_seed=None, ratio_gap=0.0, msg=0):
	"""
	Solves the given scenario using a bigm-type MIP

	Args:
		scenario:    scenario to solve
		kind:        MIP-solver to use: CPLEX, GLPK, CBC or SCIP
		bigm :       a large number to allow a big-m type model
		time_limit:  a time limit, only for CPLEX, CBC and SCIP
		random_seed: random_seed
		ratio_gap:   MIP-gap
		msg:         0 means no feedback (default) during computation, 1 means feedback

	Returns:
		scenario is solving was successful
		None if solving was not successful
	"""

	scenario.check()
	mip = MIP(str(scenario))
	return ContinuousMIP(mip).solve(scenario, bigm=bigm, kind=kind, time_limit=time_limit, random_seed=random_seed,
									ratio_gap=ratio_gap, msg=msg)


class ContinuousMIP(object):
	"""
	An interface to the pulp MIP solver package, supported are CPLEX, GLPK, CBC
	"""

	def __init__(self,mip):
		self.mip = mip
		self.scenario = None
		self.horizon = None
		self.bigm = None
		self.x = None  # mip variables shortcut


	def build_mip_from_scenario(self, task_groups=None, msg=0):

		S = self.scenario
		BIGM = self.bigm

		mip = self.mip
		#mip = pl.LpProblem(str(S), pl.LpMinimize)
		cons = list() # log of constraints for debugging

		# task variables
		x = dict()

		for T in S.tasks():
			x[T] = mip.var(str(T),up=self.horizon,cat='Continuous')#pl.LpVariable(str(T), 0)
			# add task vs resource variabls
			for RA in T.resources_req:
				for R in RA:
					x[(T, R)] = mip.var(str((T, R))) #pl.LpVariable(str((T, R)), 0, 1, cat=pl.LpBinary)

		# resources req
		for T in S.tasks():
			for RA in T.resources_req:
				if len(RA) > 1:
					continue
				affine = [ (x[(T, R)], 1) for R in RA ]
				cons.append(mip.con(affine,sense=0,rhs=1))
				#mip += sum([x[(T, R)] for R in RA]) == 1
		ra_to_tasks = S.resources_req_tasks()
		for RA in ra_to_tasks:
			tasks = list(ra_to_tasks[RA])
			T = tasks[0]
			affine = [ (x[(T, R)], 1) for R in RA ]
			cons.append(mip.con(affine,sense=0,rhs=1))
			#mip += sum([x[(T, R)] for R in RA]) == 1
			for T_ in tasks[1:]:
				for R in RA:
					affine = [ (x[(T, R)],1), (x[(T_, R)],-1) ]
					cons.append(mip.con(affine,sense=0,rhs=0))
					#mip += x[(T, R)] == x[(T_, R)]

		# objective
		affine = [ (x[T], T.completion_time_cost) for T in S.tasks()
				   if 'completion_time_cost' in T and T in x ]
		mip.obj(affine)
		#mip += pl.LpAffineExpression([ (x[T], T.completion_time_cost) for T in S.tasks()
		#                                        if 'completion_time_cost' in T and T in x ])

		# same resource variable
		task_pairs = [(T, T_) for T in S.tasks() for T_ in S.tasks() if str(T) < str(T_)]
		for (T, T_) in task_pairs:
			if T.resources:
				resources = T.resources
			else:
				resources = S.resources(task=T)
			if T_.resources:
				resources_ = T_.resources
			else:
				resources_ = S.resources(task=T_)
			shared_resources = list(set(resources) & set(resources_))

			# TODO: restrict the number of variables
			if shared_resources:
				x[(T, T_, 'SameResource')] = \
					mip.var(str((T, T_, 'SameResource')),up=S.horizon,cat='Integer')
				#   pl.LpVariable(str((T, T_, 'SameResource')), lowBound=0)  # ,cat=pl.LpInteger)
				x[(T_, T, 'SameResource')] = \
					mip.var(str((T_, T, 'SameResource')),up=S.horizon,cat='Integer')
				#   pl.LpVariable(str((T_, T, 'SameResource')), lowBound=0)  # ,cat=pl.LpInteger)
				affine = [ (x[(T, T_, 'SameResource')],1), (x[(T_, T, 'SameResource')],-1) ]
				cons.append(mip.con(affine,sense=0,rhs=0))
				#mip += x[(T, T_, 'SameResource')] == x[(T_, T, 'SameResource')]
				for R in shared_resources:
					affine = [ (x[(T, R)],1), (x[(T_, R)],1), (x[(T, T_, 'SameResource')],-1)]
					cons.append(mip.con(affine,sense=-1,rhs=1))
					#mip += x[(T, R)] + x[(T_, R)] - 1 <= x[(T, T_, 'SameResource')]
				# ordering variables
				x[(T, T_)] = mip.var(str((T, T_)))#pl.LpVariable(str((T, T_)), 0, 1, cat=pl.LpBinary)
				x[(T_, T)] = mip.var(str((T_, T)))#pl.LpVariable(str((T_, T)), 0, 1, cat=pl.LpBinary)
				affine = [ (x[(T, T_)],1), (x[(T_, T)],1)]
				cons.append(mip.con(affine,sense=0,rhs=1))
				#mip += x[(T, T_)] + x[(T_, T)] == 1

				affine = [ (x[T],1), (x[T_],-1), (x[(T, T_)],BIGM), (x[(T, T_, 'SameResource')], BIGM) ]
				cons.append(mip.con(affine,sense=-1,rhs=2*BIGM-T.length))
				#mip += x[T] + T.length <= x[T_] + \
				#           (1 - x[(T, T_)]) * BIGM + (1 - x[(T, T_, 'SameResource')]) * BIGM
				affine = [ (x[T_],1), (x[T],-1), (x[(T, T_)],-BIGM), (x[(T, T_, 'SameResource')], BIGM) ]
				cons.append(mip.con(affine,sense=-1,rhs=BIGM-T_.length))
				#mip += x[T_] + T_.length <= x[T] + \
				#        x[(T, T_)] * BIGM + (1 - x[(T, T_, 'SameResource')]) * BIGM


		# precedence constraints
		for P in S.precs_lax():
			if P.offset >= 0:
				affine = [ (x[P.task_left],1), (x[P.task_right],-1) ]
				cons.append(mip.con(affine,sense=-1,rhs=-P.task_left.length-P.offset))
				#mip += x[P.task_left] + P.task_left.length + P.offset <= x[P.task_right]
			elif P.offset < 0:
				affine = [ (x[P.task_left],1), (x[P.task_right],-1) ]
				cons.append(mip.con(affine,sense=-1,rhs=P.task_right.length-P.offset))
				#mip += x[P.task_left] <= x[P.task_right] + P.task_right.length - P.offset

		# tight precedence constraints
		for P in S.precs_tight():
			if P.offset >= 0:
				affine = [ (x[P.task_left],1), (x[P.task_right],-1) ]
				cons.append(mip.con(affine,sense=0,rhs=-P.task_left.length-P.offset))
				#mip += x[P.task_left] + P.task_left.length + P.offset == x[P.task_right]
			elif P.offset < 0:
				affine = [ (x[P.task_left],1), (x[P.task_right],-1) ]
				cons.append(mip.con(affine,sense=0,rhs=P.task_right.length-P.offset))
				#mip += x[P.task_left] == x[P.task_right] + P.task_right.length - P.offset

		# conditional precedence constraints
		for P in S.precs_cond():
			affine = [ (x[P.task_left],1), (x[P.task_right],-1),
					   (x[(P.task_left, P.task_right, 'SameResource')],BIGM) ]
			cons.append(mip.con(affine,sense=-1,rhs=-P.task_left.length-P.offset+1*BIGM))
			#mip += x[P.task_left] + P.task_left.length + P.offset <= x[P.task_right] + \
			#                   (1 - x[(P.task_left, P.task_right)]) * BIGM + (1 - x[
			#   (P.task_left, P.task_right, 'SameResource')]) * BIGM

		# upper bounds
		for P in S.bounds_up():
			affine = [ (x[P.task],1) ]
			cons.append(mip.con(affine,sense=-1,rhs=P.bound-P.task.length))
			#mip += x[P.task] + P.task.length <= P.bound

		# lower bounds
		for P in S.bounds_low():
			affine = [ (x[P.task],1) ]
			cons.append(mip.con(affine,sense=1,rhs=P.bound))
			#mip += x[P.task] >= P.bound

		# tight upper bounds
		for P in S.bounds_up_tight():
			affine = [ (x[P.task],1) ]
			cons.append(mip.con(affine,sense=0,rhs=P.bound-P.task.length))
			#mip += x[P.task] + P.task.length == P.bound

		# tight lower bounds
		for P in S.bounds_low_tight():
			affine = [ (x[P.task],1) ]
			cons.append(mip.con(affine,sense=0,rhs=P.bound))
			#mip += x[P.task] == P.bound

		'''
		# capacity lower bounds
		for C in S.capacity_low():
			# ignore sliced capacity constraints
			if C._start != None or C._end != None:
				continue
			affine = [ (x[T, C.resource], C.weight(T=T,t=0)) for T in S.tasks()
					   if (T,C.resource) in x and C.weight(T=T,t=0) ]
			if not affine:
				continue
			cons.append(mip.con(affine, sense=1, rhs=C.bound))

		# capacity upper bounds
		for C in S.capacity_up():
			# ignore sliced capacity constraints
			if C._start != None or C._end != None:
				continue
			affine = [ (x[T, C.resource], C.weight(T=T,t=0)) for T in S.tasks()
					   if (T,C.resource) in x and C.weight(T=T,t=0) ]
			if not affine:
				continue
			cons.append(mip.con(affine, sense=-1, rhs=C.bound))
		'''

		'''
		for con in cons:
			mip.add_con(con)
		'''

		self.mip = mip
		self.x = x

	def read_solution_from_mip(self, msg=0):
		for T in self.scenario.tasks():
			if self.x[T].varValue is None:
				T.start_value = 0
			else:
				T.start_value = int(self.x[T].varValue)
			if T.resources:
				resources = T.resources
			else:
				resources = self.scenario.resources(task=T)

			task_resources = []
			for resource in resources:
				value = self.mip.value(self.x[(T,resource)])
				if value != None and value > 0:
					task_resources.append(resource)
			T.resources = task_resources

	def solve(self, scenario, bigm=10000, kind='CBC', time_limit=None, random_seed=None, ratio_gap=0.0, msg=0):

		self.scenario = scenario
		self.horizon = self.scenario.horizon
		self.bigm = bigm
		self.build_mip_from_scenario(msg=msg)

		params = dict()
		if time_limit is not None:
			params['time_limit'] = str(time_limit)
		if random_seed is not None:
			params['random_seed'] = str(random_seed)
		params['kind']= kind
		params['ratio_gap'] = str(ratio_gap)
		self.mip.solve(msg=msg,**params)
		#_solve_mip(self.mip, kind=kind, params=params, msg=msg)

		if self.mip.status() == 1:
			self.read_solution_from_mip(msg=msg)
			return 1
		if msg:
			print('ERROR: no solution found')
		return 0
