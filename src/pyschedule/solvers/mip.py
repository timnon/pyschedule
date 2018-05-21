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
		kind:                MIP-solver to use: CPLEX, GLPK, CBC, SCIP, GUROBI
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
			# single resource assignments restrict the periods directly
			task_periods = set(T.periods)
			task_resources_periods = [ set(R.periods)
				for RA in T.resources_req if len(RA) == 1
				for R in RA ]
			if task_resources_periods:
				task_periods &= set.intersection(*task_resources_periods)
			x.update({ (T,t) : mip.var(str((T, t)), 0, task_group_size, cat) for t in task_periods })
			affine = [(x[T, t], 1) for t in task_periods ]
			# check if task is required
			if T.schedule_cost is None:
				cons.append(mip.con(affine, sense=0, rhs=task_group_size))
			else:
				cons.append(mip.con(affine, sense=-1, rhs=task_group_size))

			for RA in T.resources_req:
				# check if contains a single resource
				if len(RA) <= 1:
					continue
				# create variables if necessary except the first one
				x.update({ (T,R,t) : mip.var(str((T, R, t)), 0, task_group_size, cat)
						   for R in RA for t in R.periods if (T,R,t) not in x})
				# enough position needs to get selected
				# synchronize with base variables
				for t in task_periods:
					affine = [(x[T, R, t], 1) for R in RA if (T,R,t) in x ] + [(x[T,t],-1)]
					cons.append(mip.con(affine, sense=0, rhs=0))

			# generate shortcuts for single resources
			x.update({ (T,R,t) : x[T,t]
				for RA in T.resources_req if len(RA) == 1
				for R in RA for t in task_periods })

		# synchronize in RA with multiple tasks
		ra_to_tasks = S.resources_req_tasks()
		for RA in ra_to_tasks:
			tasks = list(set(ra_to_tasks[RA]) & set(self.task_groups))
			if not tasks:
				continue
			for R in RA:
				T_ = tasks[0]
				for T in tasks[1:]:
					affine = [(x[T,R,t],1) for t in R.periods ]+\
							 [(x[T_,R,t],-1) for t in R.periods ]
					cons.append(mip.con(affine, sense=0, rhs=0))

		# everybody is finished before the horizon TODO: why is this check necessary
		affine = [ (x[T, t],1) for T in S.tasks()
		           for t in range(self.horizon-T.length+1,self.horizon)
				   if (T,t) in x ]
		cons.append(mip.con(affine, sense=-1, rhs=0))

		# tasks are not allowed to be scheduled in the same resource at the same time
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

			# case for tasks of length zero, they can block longer tasks
			for t in range(1,self.horizon):
				affine =  [(x[T, R, t_], coeffs[T,R])
						   for T in set(S.tasks(resource=R)) & set(self.task_groups)
						   for t_ in range(t+1-T.length,t+1)
						   if T.length > 1 and (T,R,t_) in x ]
				affine += [(x[T, R, t], coeffs[T,R])
						   for T in set(S.tasks(resource=R)) & set(self.task_groups)
						   if T.length == 0 and (T,R,t) in x ]
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
			#covers the case that the right task group has size one
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
			affine =  [(x[P.task, t],1) for t in range(P.bound)]
			affine += [(x[P.task, t],1) for t in range(P.bound+1,self.horizon)]
			cons.append(mip.con(affine, sense=0, rhs=0))

		# tight up bounds
		for P in S.bounds_up_tight():
			if P.task not in self.task_groups:
				continue
			affine =  [(x[P.task, t],1) for t in range(P.bound-P.task.length)]
			affine += [(x[P.task, t],1) for t in range(P.bound-P.task.length+1,self.horizon)]
			cons.append(mip.con(affine, sense=0, rhs=0))

		# conditional precedence constraints
		for P in S.precs_cond():
			if P.task_left not in self.task_groups or P.task_right not in self.task_groups:
				continue
			left_size = float(len(self.task_groups[P.task_left]))
			right_size = float(len(self.task_groups[P.task_right]))
			shared_resources = list(set(S.resources(task=P.task_left)) & set(S.resources(task=P.task_right)))
			for R in shared_resources:
				if left_size == 1:
					for t in range(1,self.horizon):
						# if the sum of x[P.task_left, R, t_] is one, then there is
						# no slack in the next constraint (1 in coefficient), and
						# then the monotonicity defined by -1*(t_<t-P.offset-P.task_left.length)
						# needs to get saisfied
						affine = \
							[(x[P.task_left, R, t_],1-1*(t_<t-P.offset-P.task_left.length)) for t_ in R.periods ] + \
							[(x[P.task_right, R, t_],1/right_size) for t_ in R.periods if t_ < t ]
						cons.append(mip.con(affine, sense=-1, rhs=1))
				elif right_size == 1:
					for t in range(self.horizon):
						affine = \
							[(x[P.task_left, R, t_],1/left_size) for t_ in R.periods if t_ >= t ] + \
							[(x[P.task_right, R, t_],1-1*(t_>=t+P.offset+P.task_left.length)) for t_ in R.periods ]
						cons.append(mip.con(affine, sense=-1, rhs=1))
				else:
					print('ERROR: at least one task group in conditional precedence constraint should have size 1')

		# capacity upper and lower bounds
		for C in S.capacity_up() + S.capacity_low():
			R = C.resource
			if C._start is not None:
				start = C._start
			else:
				start = 0
			if C._end is not None:
				end = C._end
			else:
				end = S.horizon
			affine = [ (x[T,R,t-T.length+1], C.weight(T,t-T.length+1))
					  for t in range(start,end)
					  for T in self.task_groups
					  if (T,R,t-T.length+1) in x and C.weight(T,t-T.length+1) ]
			if not affine:
				continue
			# sum up (pulp doesnt do this)
			affine_ = { a:0 for a,b in affine }
			for a,b in affine:
				affine_[a] += b
			affine = [ (a,affine_[a]) for a in affine_ ]
			if C in S.capacity_up():
				sense = -1
			else:
				sense = 1
			cons.append(mip.con(affine, sense=sense, rhs=C.bound))

		# capacity switch bounds
		for count, C in enumerate(S.capacity_diff_up()):
			R = C.resource

			def get_diff_con(count,C,t,flip):
				affine_1 =  [ (x[T,R,t-T.length+1],flip*C.weight(T)) for T in self.task_groups
						   if (T,R,t-T.length+1) in x and C.weight(T) ]
				affine_2 = [ (x[T,R,t+1],-flip*C.weight(T)) for T in self.task_groups
						   if (T,R,t+1) in x and C.weight(T) ]
				if affine_1 and affine_2:
					if ('switch_%i'%count,R,t) not in x:
						x['switch_%i'%count,R,t] = mip.var(str(('switch_%i'%count,R, t)), 0, C.bound)
					affine = affine_1 + affine_2 + [ (x['switch_%i'%count,R,t],1) ]
					con = mip.con(affine, sense=1, rhs=0)
					return con
				return None

			if C._start is not None:
				start = C._start
			else:
				start = 0
			if C._end is not None:
				end = C._end
			else:
				end = S.horizon
			for t in range(start,end-1):
				if C.kind == 'diff' or C.kind == 'diff_dec':
					con = get_diff_con(count,C,t,-1)
					if con is not None:
						cons.append(con)
				if C.kind == 'diff' or C.kind == 'diff_inc':
					con = get_diff_con(count,C,t,1)
					if con is not None:
						cons.append(con)
			affine = [ (x['switch_%i'%count,R,t],1) for t in range(S.horizon) if ('switch_%i'%count,R,t) in x ]
			if affine:
				cons.append(mip.con(affine, sense=-1, rhs=C.bound))

		def task2cost(T,t):
			cost = 0
			if T.completion_time_cost is not None:
				cost += T.completion_time_cost*t
			if T.schedule_cost is not None:
				cost += T.schedule_cost
			return cost

		objective = [
			(x[T, t], task2cost(T,t))
			for T in S.tasks()
			if T in self.task_groups
			for t in T.periods if (T,t) in x ]

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
				# in case of not required tasks with schedule_cost, there might be less starts than tasks
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

		#print([ self.x[scenario['T1_e'],scenario['R1'],i].value() for i in range(scenario.horizon) ])
		#print([ self.x[scenario['T0'],scenario['R1'],i].value() for i in range(scenario.horizon) ])
		#_solve_mip(self.mip, kind=kind, params=params, msg=msg)

		if self.mip.status() == 1:
			self.read_solution_from_mip(msg=msg)
			return 1
		if msg:
			print('ERROR: no solution found')
		return 0
