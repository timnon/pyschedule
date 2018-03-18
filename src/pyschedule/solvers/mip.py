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



def _isnumeric(var):
	return isinstance(var, (int))  # only integers are accepted

def _get_task_groups(scenario):
	"""
	computes the task groups according to the _task_group parameter
	returns a mapping a task group representative to the task group
	"""
	_task_groups = collections.OrderedDict()
	for T in scenario.tasks():
		if 'group' in T:
			task_group_name = T.group
			if task_group_name in _task_groups:
				_task_groups[task_group_name].append(T)
			else:
				_task_groups[task_group_name] = [T]
	task_groups = collections.OrderedDict([ (_task_groups[task_group_name][0],
											 _task_groups[task_group_name])
										  for task_group_name in _task_groups])
	tasks_in_task_groups = [ T_ for T in task_groups for T_ in task_groups[T] ]
	task_groups.update([ (T,[T]) for T in scenario.tasks()
								 if T not in tasks_in_task_groups ])
	return task_groups

def solve(scenario, kind='CBC', time_limit=None, random_seed=None, ratio_gap=0.0, msg=0):
	"""
	Solves the given scenario using a discrete MIP

	Args:
		scenario:            scenario to solve
		kind:                MIP-solver to use: CPLEX, GLPK, CBC, SCIP
		time_limit:          a time limit, only for CPLEX, CBC and SCIP
		random_seed:         random seed
		ratio_gap:           MIP-gap
		msg:                 0 means no feedback (default) during computation, 1 means feedback

	Returns:
		1 if solving was successful
		0 if solving was not successful
	"""
	scenario.check()
	mip = MIP(str(scenario))
	return DiscreteMIP(mip).solve(scenario, kind=kind, time_limit=time_limit, random_seed=random_seed, ratio_gap=ratio_gap, msg=msg)

def solve_bigm(scenario, bigm=10000, kind='CBC', time_limit=None, random_seed=None, ratio_gap=0.0, msg=0):
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
			affine = [ (x[P.task_left],1), (x[P.task_right],-1), (x[(P.task_left, P.task_right)],BIGM),
					   (x[(P.task_left, P.task_right, 'SameResource')],BIGM) ]
			cons.append(mip.con(affine,sense=-1,rhs=-P.task_left.length-P.offset+2*BIGM))
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



class DiscreteMIP(object):
	"""
	pulp with time discretisation
	"""

	def __init__(self,mip):
		self.mip = mip
		self.scenario = None
		self.horizon = None
		self.task_groups = None
		self.x = None  # mip variables shortcut

	def build_mip_from_scenario(self, msg=0):
		S = self.scenario
		mip = self.mip
		self.task_groups = _get_task_groups(self.scenario)

		x = dict()  # mip variables
		cons = list()  # log of constraints for debugging
		for T in self.task_groups:
			task_group_size = len(self.task_groups[T])
			# base time-indexed variables
			cat = 'Binary'
			if task_group_size > 1:
				cat = 'Integer'
			x.update({ (T,t) : mip.var(str((T, t)), 0, task_group_size, cat) for t in range(self.horizon) })
			affine = [(x[T, t], 1) for t in range(self.horizon) ]

			# check if task is required
			if T.reward is None:
				cons.append(mip.con(affine, sense=0, rhs=task_group_size))
			else:
				cons.append(mip.con(affine, sense=-1, rhs=task_group_size))

			for RA in T.resources_req:
				# check if contains a single resource
				if len(RA) <= 1:
					continue
				# create variables if necessary except the first one
				x.update({ (T,R,t) : mip.var(str((T, R, t)), 0, task_group_size, cat)
						   for R in RA for t in range(self.horizon) if (T,R,t) not in x})
				# enough position needs to get selected
				affine = [(x[T, R, t], 1) for R in RA for t in range(self.horizon) ]
				# TODO: can the next line be removed?
				# cons.append(mip.con(affine, sense=0, rhs=task_group_size))
				# synchronize with base variables
				for t in range(self.horizon):
					affine = [(x[T, R, t], 1) for R in RA] + [(x[T,t],-1)]
					cons.append(mip.con(affine, sense=0, rhs=0))

			# generate shortcuts for single resources
			x.update({ (T,R,t) : x[T,t] for RA in T.resources_req if len(RA) == 1
					   for R in RA for t in range(self.horizon) })

		# synchronize in RA with multiple tasks
		ra_to_tasks = S.resources_req_tasks()
		for RA in ra_to_tasks:
			tasks = list(set(ra_to_tasks[RA]) & set(self.task_groups))
			if not tasks:
				continue
			for R in RA:
				T_ = tasks[0]
				for T in tasks[1:]:
					affine = [(x[T,R,t],1) for t in range(self.horizon) ]+\
							 [(x[T_,R,t],-1) for t in range(self.horizon) ]
					cons.append(mip.con(affine, sense=0, rhs=0))

		# everybody is finished before the horizon TODO: why is this check necessary
		affine = [ (x[T, t],1) for T in S.tasks() for t in range(self.horizon-T.length+1,self.horizon) if (T,t) in x ]
		cons.append(mip.con(affine, sense=-1, rhs=0))

		coeffs = { (T,R) : RA[R] for T in S.tasks() for RA in T.resources_req for R in RA }
		for R in S.resources():
			if R.size is not None:
				resource_size = R.size
			else:
				resource_size = 1.0
			for t in range(self.horizon):
				affine = [(x[T, R, t_], coeffs[T,R])
						  for T in set(S.tasks(resource=R)) & set(self.task_groups)
						  for t_ in range(t+1-T.length,t+1)
						  if (T,R,t_) in x ]
				cons.append(mip.con(affine, sense=-1, rhs=resource_size))

		# lax precedence constraints
		for P in S.precs_lax():
			if P.task_left not in self.task_groups or P.task_right not in self.task_groups:
				continue
			left_size = float(len(self.task_groups[P.task_left]))
			right_size = float(len(self.task_groups[P.task_right]))
			#in the default case it is expected that the task groups have similar
			#size, so the first task in the left task group must be scheduled before
			#the first task in the right task group, and so on
			if left_size == right_size:
				for t in range(max(-P.task_left.length-P.offset,0),min(self.horizon-P.task_left.length-P.offset,self.horizon)) :
					affine = \
						[(x[P.task_left, t_],1) for t_ in range(t,self.horizon)] + \
						[(x[P.task_right, t_],-1) for t_ in range(t+P.task_left.length+P.offset,self.horizon)]
					cons.append(mip.con(affine, sense=-1, rhs=0))
			#covers the case that the right task group has size ones
			#in which case this task should be scheduled after all tasks in the
			#left task group
			elif left_size == 1 or right_size == 1:
				for t in range(max(P.task_left.length+P.offset,0),min(self.horizon+P.task_left.length+P.offset,self.horizon)):
					affine = \
						[(x[P.task_left, t_],1/left_size) for t_ in range(t,self.horizon)] + \
						[(x[P.task_right, t_],-1/right_size) for t_ in range(t+P.task_left.length+P.offset,self.horizon)]
					cons.append(mip.con(affine, sense=-1, rhs=0))
			#covers the cases that the task groups have different sizes != 1
			#if the right task group is larger, then the  additonal tasks
			#will have no contraints
			else:
				for t in range(max(P.task_left.length+P.offset,0),min(self.horizon+P.task_left.length+P.offset,self.horizon)):
					affine = \
						[(x[P.task_left, t_],1) for t_ in range(t-P.task_left.length-P.offset)] + \
						[(x[P.task_right, t_],-1) for t_ in range(t)]
					cons.append(mip.con(affine, sense=1, rhs=0))

		# tight precedence constraints
		for P in S.precs_tight():
			if P.task_left not in self.task_groups or P.task_right not in self.task_groups:
				continue
			'''
			if P.offset >= 0:
				affine = [(x[P.task_left, t],t) for t in range(self.horizon)] + \
					 [(x[P.task_right, t],-t) for t in range(self.horizon)]
				pulpmip.cons(affine, sense=0, rhs=-(P.task_left.length + P.offset))
			elif P.offset < 0:
				affine = [(x[P.task_left, t],t) for t in range(self.horizon)] +\
					 [(x[P.task_right, t],-t) for t in range(self.horizon)]
				pulpmip.cons(affine, sense=0, rhs= P.task_right.length-P.offset )
			'''
			if P.offset >= 0:
				for t in range(self.horizon):
					affine = [(x[P.task_left, t_],1) for t_ in range(t,self.horizon)] + \
						 [(x[P.task_right, t_],-1) for t_ in range(min(t+P.task_left.length+P.offset,self.horizon),self.horizon)]
					cons.append(mip.con(affine, sense=0, rhs=0))
			elif P.offset < 0:
				for t in range(self.horizon):
					affine = [(x[P.task_right, t_],1) for t_ in range(t)] + \
						 [(x[P.task_left, t_],-1) for t_ in range(min(t+P.task_right.length-P.offset,self.horizon))]
					cons.append(mip.con(affine, sense=0, rhs=0))

		# low bounds
		for P in S.bounds_low():
			if P.task not in self.task_groups:
				continue
			affine = [(x[P.task, t],1) for t in range(P.bound)]
			cons.append(mip.con(affine, sense=0, rhs=0))

		# up bounds
		for P in S.bounds_up():
			if P.task not in self.task_groups:
				continue
			affine = [(x[P.task, t],1) for t in range(max(P.bound-P.task.length+1,0),self.horizon)]
			cons.append(mip.con(affine, sense=0, rhs=0))

		# tight low bounds
		for P in S.bounds_low_tight():
			if P.task not in self.task_groups:
				continue
			task_group_size = len(self.task_groups[P.task])
			cons.append(mip.con([(x[P.task, P.bound],1)], sense=0, rhs=task_group_size))

		# tight up bounds
		for P in S.bounds_up_tight():
			if P.task not in self.task_groups:
				continue
			task_group_size = len(self.task_groups[P.task])
			cons.append(mip.con([(x[P.task, max(P.bound-P.task.length,0)],1)], sense=0, rhs=task_group_size))

		# conditional precedence constraints
		for P in S.precs_cond():
			if P.task_left not in self.task_groups or P.task_right not in self.task_groups:
				continue
			shared_resources = list(set(S.resources(task=P.task_left)) & set(S.resources(task=P.task_right)))
			for R in shared_resources:
				for t in range(self.horizon):
					affine = [(x[P.task_left, R, t], 1)] +\
							 [(x[P.task_right, R, t_],1)
							  for t_ in range(t,min(t+P.task_left.length+P.offset,self.horizon))]
					rhs = (len(self.task_groups[P.task_left])+len(self.task_groups[P.task_right])/2.0)
					cons.append(mip.con(affine, sense=-1, rhs=rhs))

		# capacity lower bounds
		for C in S.capacity_low():
			# weight gets proportionally assigned according to overlap
			affine = [ (x[T, C.resource, t_], C.weight(T=T,t=t)/float(T.length) )
					  for t in range(self.horizon)
					  for T in self.task_groups
					  for t_ in range(max(0,t-T.length+1),t+1)
					  if (T,C.resource,t_) in x and C.weight(T=T,t=t) ]
			'''
			affine = [ (x[T, C.resource, t], C.weight(T=T,t=t)) for T in self.task_groups
					  for t in range(self.horizon) if (T,C.resource,t) in x and C.weight(T=T,t=t) ]
			'''
			if not affine:
				continue
			# sum up (pulp doesnt do this)
			affine_ = { a:0 for a,b in affine }
			for a,b in affine:
				affine_[a] += b
			affine = [ (a,affine_[a]) for a in affine_ ]
			cons.append(mip.con(affine, sense=1, rhs=C.bound))

		# capacity upper bounds
		for C in S.capacity_up():
			# weight gets proportionally assigned according to overlap
			affine = [ (x[T, C.resource, t_], C.weight(T=T,t=t)/float(T.length) )
					  for t in range(self.horizon)
					  for T in self.task_groups
					  for t_ in range(max(0,t-T.length+1),t+1)
					  if (T,C.resource,t_) in x and C.weight(T=T,t=t) ]
			'''
			affine = [ (x[T, C.resource, t], C.weight(T=T,t=t)) for T in self.task_groups
					  for t in range(self.horizon) if (T,C.resource,t) in x and C.weight(T=T,t=t) ]
			'''
			if not affine:
				continue
			# sum up (pulp doesnt do this)
			affine_ = { a:0 for a,b in affine }
			for a,b in affine:
				affine_[a] += b
			affine = [ (a,affine_[a]) for a in affine_ ]
			cons.append(mip.con(affine, sense=-1, rhs=C.bound))

		# capacity switch bounds
		count = 0
		for C in S.capacity_diff_up():
			R = C.resource
			# get affected periods
			periods = list(set([ t for t in range(self.horizon) for T in self.task_groups if C.weight(T,t) ]))
			periods = sorted(periods)
			x.update({ ('switch_%i'%count,R,t) : mip.var(str(('switch_%i'%count,R, t)), 0, 1)
					   for t in periods })
			# define switch variables
			for t in periods[:-1]:
				# decrease switch
				if C.kind == 'diff' or C.kind == 'diff_dec':
					affine = [ (x['switch_%i'%count,R,t],1) ] +\
							 [ (x[T,R,t-T.length+1],-1) for T in self.task_groups
							   if (T,R,t-T.length+1) in x and C.weight(T,t) ] +\
							 [ (x[T,R,t+1],1) for T in self.task_groups
							   if (T,R,t+1) in x and C.weight(T,t+1) ]
					cons.append(mip.con(affine, sense=1, rhs=0))
				# increase switch
				if C.kind == 'diff' or C.kind == 'diff_inc':
					affine = [ (x['switch_%i'%count,R,t],1) ] +\
							 [ (x[T,R,t-T.length+1],1) for T in self.task_groups
							   if (T,R,t-T.length+1) in x and C.weight(T,t) ] +\
							 [ (x[T,R,t+1],-1) for T in self.task_groups
							   if (T,R,t+1) in x and C.weight(T,t+1) ]
					cons.append(mip.con(affine, sense=1, rhs=0))
			affine = [ (x['switch_%i'%count,R,t],1) for t in periods[:-1] if ('switch_%i'%count,R,t) in x ]
			cons.append(mip.con(affine, sense=-1, rhs=C.bound))
			count += 1

		def task2cost(T,t):
			cost = 0
			if T.completion_time_cost is not None:
				cost += T.completion_time_cost*t
			if T.reward is not None:
				cost -= T.reward
			return cost

		objective = [
			(x[T, t], task2cost(T,t))
			for T in S.tasks()
			if T in self.task_groups
			for t in range(self.horizon) ]

		mip.obj(objective)
		'''
		for con in cons:
			mip.add_con(con)
		'''
		self.mip = mip
		self.x = x


	def read_solution_from_mip(self, msg=0):
		for T in self.task_groups:
			# get all possible starts with combined resources
			starts = \
				[ (t,R)
				for t in range(self.horizon)
				for R in self.scenario.resources()
				if (T,R,t) in self.x and self.mip.value(self.x[T, R, t]) is not None
				for i in range(int(self.mip.value(self.x[T, R, t])))
				]

			# iteratively assign starts and resources
			for T_ in self.task_groups[T]:
				# reset values
				T_.start_value = None
				T_.resources = list()
				# in case of not required tasks with reward, there might be less starts than tasks
				if not starts:
					break
				# consider single resources first
				RAs = [ RA for RA in T_.resources_req if len(RA) == 1 ] + \
					  [ RA for RA in T_.resources_req if len(RA) > 1  ]
				T_.start_value = [ t for (t, R) in starts ][0]
				for RA in RAs :
					if set(T_.resources) & set(RA):
						continue
					(t, R) = [(t_, R_) for (t_, R_) in starts if R_ in RA and t_ == T_.start_value][0]
					starts.remove((t, R))
					T_.resources.append(R)


	def solve(self, scenario, kind='CBC', time_limit=None, random_seed=None, ratio_gap=0.0, msg=0):

		self.scenario = scenario
		if self.scenario.horizon is None:
			raise Exception('ERROR: solver requires scenarios with defined horizon')
			return 0
		self.horizon = self.scenario.horizon
		self.build_mip_from_scenario(msg=msg)

		# if time_limit :
		#   options += ['sec',str(time_limit),'ratioGap',str(0.1),'cuts','off',
				#       'heur','on','preprocess','on','feas','on']#,'maxNodes',str(0),'feas','both','doh','solve']

		params = dict()
		if time_limit is not None:
			params['time_limit'] = time_limit
		if random_seed is not None:
			params['random_seed'] = str(random_seed)
		#params['cuts'] = 'off'
		params['ratio_gap'] = str(ratio_gap)
		params['kind'] = kind
		self.mip.solve(msg=msg,**params)

		#_solve_mip(self.mip, kind=kind, params=params, msg=msg)

		if self.mip.status() == 1:
			self.read_solution_from_mip(msg=msg)
			return 1
		if msg:
			print('ERROR: no solution found')
		return 0
