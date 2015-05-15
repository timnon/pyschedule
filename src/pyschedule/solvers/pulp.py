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

import time, copy, collections
import pulp as pl


def _solve_mip(mip,kind='CBC',time_limit=None,msg=0) :

	start_time = time.time()
	# select solver for pl
	if kind == 'CPLEX' :
		if time_limit :
			# pulp does currently not support a timelimit in 1.5.9
			mip.solve(pl.CPLEX_CMD(msg=msg,timelimit=time_limit))
		else :
			mip.solve(pl.CPLEX_CMD(msg=msg))
	elif kind == 'GLPK' :
		mip.solve(pl.GLPK_CMD(msg=msg))
	elif kind == 'CBC' :
		options = []
		if time_limit :
			options += ['sec',str(time_limit)]
		mip.solve(pl.PULP_CBC_CMD(msg=msg,options=options))
	else :
		raise Exception('ERROR: solver '+kind+' not known')

	if msg :
		print('INFO: execution time for solving mip (sec) = '+str(time.time()-start_time))
	if mip.status == 1 and msg :		
		print('INFO: objective = '+str(pl.value(mip.objective)))


def solve(scenario,big_m=10000,kind='CBC',time_limit=None,msg=0,return_copy=False) :
	"""
	Shortcut to continuous mip
	"""
	if return_copy :
		scenario = copy.deepcopy(scenario)
	ContinuousMIP().solve(scenario,big_m=big_m,kind=kind,time_limit=time_limit,msg=msg)
	return scenario


def solve_discrete(scenario,horizon,kind='CBC',time_limit=None,task_groups=None,msg=0,return_copy=False) :
	"""
	Shortcut to discrete mip
	"""
	if return_copy :
		scenario = copy.deepcopy(scenario)
	DiscreteMIP().solve(scenario,horizon,kind=kind,time_limit=time_limit,task_groups=task_groups,msg=msg)
	return scenario


class ContinuousMIP(object) :
	"""
	An interface to the pulp MIP solver package, supported are CPLEX, GLPK, CBC
	"""

	def __init__(self) :
		self.scenario = None
		self.big_m = None
		self.mip = None
		self.x = None  # mip variables shortcut


	def build_mip_from_scenario(self,task_groups=None,msg=0) :

		S = self.scenario
		BIG_M = self.big_m #TODO: GLPK has problems with large number
		mip = pl.LpProblem(str(S), pl.LpMinimize)

		# check for objective
		if not S.objective() :
			if msg : print('INFO: use makespan objective as default')
			S.use_makespan_objective()

		# task variables
		x = dict()

		for T in S.tasks() :
			x[T] = pl.LpVariable(T,0)

			# fix variables if start is given (0.0 is also False!)
			if T.start is not None :
				mip += x[T] == T.start

			# add assignment variable for each possible resource
			# if resources are fixed take only these
			if T.resources :
				for R in T.resources :
					x[(T,R)] = pl.LpVariable((T,R),0,1,cat=pl.LpBinary)
					mip += x[(T,R)] == 1
			else :
				for R in T.resources_req.resources() :
					x[(T,R)] = pl.LpVariable((T,R),0,1,cat=pl.LpBinary)
				# everybody is required on one resource from each or clause
				for RA in T.resources_req :
					mip += sum([ x[(T,R)] for R in RA ]) == 1

		# objective
		objective = S.objective()
		mip += sum([ x[T]*objective[T] for T in objective if T in x ])

		# resource capacity constraints
		for R in S.resources() :
			if R.capacity :
				mip += sum([ x[(T,R)]*T.resources_req.capacity(R) for T in S.tasks() \
		                               if R in T.resources_req.resources() ]) <= R.capacity

		# same resource variable
		task_pairs = [ (T,T_) for T in S.tasks() for T_ in S.tasks() if str(T) < str(T_) ]
		for (T,T_) in task_pairs :
			if T.resources :
				resources = T.resources
			else :
				resources = T.resources_req.resources()
			if T_.resources :
				resources_ = T_.resources
			else :
				resources_ = T_.resources_req.resources()
			shared_resources = list( set(resources) & set(resources_) )
			# TODO: restrict the number of variables
			if shared_resources and (T.start is None or T_.start is None ) :
				x[(T,T_,'SameResource')] = pl.LpVariable((T,T_,'SameResource'),lowBound=0)#,cat=pl.LpInteger)
				x[(T_,T,'SameResource')] = pl.LpVariable((T_,T,'SameResource'),lowBound=0)#,cat=pl.LpInteger)
				mip += x[(T,T_,'SameResource')] == x[(T_,T,'SameResource')]
				for R in shared_resources :
					mip += x[(T,R)] + x[(T_,R)] - 1 <= x[(T,T_,'SameResource')]
				# ordering variables
				x[(T,T_)] = pl.LpVariable((T,T_),0,1,cat=pl.LpBinary)
				x[(T_,T)] = pl.LpVariable((T_,T),0,1,cat=pl.LpBinary)
				mip += x[(T,T_)] + x[(T_,T)] == 1

				mip += x[T] + T.length <= x[T_] + (1-x[(T,T_)])*BIG_M + (1-x[(T,T_,'SameResource')])*BIG_M 
				mip += x[T_] + T_.length <= x[T] + x[(T,T_)]*BIG_M + (1-x[(T,T_,'SameResource')])*BIG_M
			
		
		# precedence constraints
		for P in S.precs_lax() :
			# if at least one of the tasks is not fixed
			if P.left.start is None or P.right.start is None :
				mip += x[P.left] + P.left.length + P.offset <= x[P.right] 
	
	
		# tight precedence constraints
		for P in S.precs_tight() :
			# if at least one of the tasks is not fixed
			if P.left.start is None and P.right.start is None :
				mip += x[P.left] + P.left.length + P.offset == x[P.right] 

		# TODO: not set if not on same resource??
		# conditional precedence constraints
		for P in S.precs_cond() :
			# if at least one of the tasks is not fixed
			if P.left.start is None and P.right.start is None :
				mip += x[P.left] + P.left.length + P.offset <= x[P.right] + \
			                (1-x[(P.left,P.right)])*BIG_M + (1-x[(P.left,P.right,'SameResource')])*BIG_M

		# upper bounds
		for P in S.precs_up() :
			# if start is not fixed
			if P.left.start is None :
				mip += x[P.left] + P.left.length <= P.right

		# lower bounds
		for P in S.precs_low() :
			# if start is not fixed
			if P.left.start is None :
				mip += x[P.left] >= P.right

		self.mip = mip
		self.x = x


	def read_solution_from_mip(self,msg=0) :
		for T in self.scenario.tasks() :
			T.start = self.x[T].varValue
			if T.resources :
				resources = T.resources
			else :
				resources = T.resources_req.resources()
			T.resources = [ R for R in resources if self.x[(T,R)].varValue > 0 ]


	def solve(self,scenario,big_m=10000,kind='CBC',time_limit=None,msg=0) :
		"""
		Solves the given scenario using a continous MIP via the pulp package

		Args:
			scenario:    scenario to solve
			kind:        MIP-solver to use: CPLEX, GLPK, CBC
			big_m :      a large number to allow a big-m type model
			time_limit:  a time limit, only for CPLEX and CBC
			msg:         0 means no feedback (default) during computation, 1 means feedback
	
		Returns:
			scenario is solving was successful
			None if solving was not successful
		"""
		self.scenario = scenario
		self.big_m = big_m
		self.build_mip_from_scenario(msg=msg)
		_solve_mip(self.mip, kind=kind, time_limit=time_limit, msg=msg)

		if self.mip.status != 1 :
			if msg : print('ERROR: no solution found')
			#return None #TODO: problem sometimes still returned 0 when solution found

		self.read_solution_from_mip(msg=msg)
		return self.scenario


class DiscreteMIP(object) :
	"""
	pulp with time discretisation
	"""

	def __init__(self) :
		self.scenario = None
		self.horizon = None
		self.task_groups = None
		self.mip = None
		self.x = None  # mip variables shortcut


	def build_mip_from_scenario(self,msg=0) :
		S = self.scenario
		MAX_TIME = self.horizon
		mip = pl.LpProblem(str(S), pl.LpMinimize)

		# check for objective
		if not S.objective() :
			if msg : print('INFO: use makespan objective as default')
			S.use_makespan_objective()
		

		# organize task groups
		if self.task_groups == None :
			self.task_groups = collections.OrderedDict()
		tasks_in_groups = set([ T for group in self.task_groups for T in self.task_groups[group] ])
		for T in S.tasks() :
			if T not in tasks_in_groups :
				self.task_groups[T] = [T]
		task_to_group = { T_ : T for T in self.task_groups for T_ in self.task_groups[T] }



		# task variables
		x = dict()
		cons = list()
		for T in self.task_groups :
			task_group_size = len(self.task_groups[T])

			for t in range(MAX_TIME) :
				if T.resources_req.resources() :
					x[(T,t)] = pl.LpVariable((T,t),0,task_group_size)
				else :
					x[(T,t)] = pl.LpVariable((T,t),0,task_group_size,cat=pl.LpInteger) # integer in case no resource is required

			# monotonicity (needed for tasks without resource,e.g. makespan)
			for t in range(MAX_TIME-1) :
				cons.append( pl.LpConstraint( pl.LpAffineExpression([ (x[(T,t)],1), (x[(T,t+1)],-1) ]), sense=1, rhs=0 ) )
	

			# lower and upper boundary conditions
			cons.append( pl.LpConstraint( x[(T,0)], sense=0, rhs=task_group_size ) )
			cons.append( pl.LpConstraint( x[(T,self.horizon-1)], sense=0, rhs=0 ) ) #required for no solution feedback

			# generate variabels for task resources
			for R in T.resources_req.resources() :
				# variables
				for t in range(MAX_TIME) :
					x[(T,R,t)] = pl.LpVariable((T,R,t),0,task_group_size,cat=pl.LpInteger) #binary or not?
				# monotonicity
				for t in range(MAX_TIME-1) :
					cons.append( pl.LpConstraint( pl.LpAffineExpression([ (x[(T,R,t)],1), (x[(T,R,t+1)],-1) ]), sense=1, rhs=0 ) )

			affine = pl.LpAffineExpression([ (x[(T,R,t)],1) for R in T.resources_req.resources() ] + [(x[(T,t)],-1)])
			cons.append( pl.LpConstraint( affine, sense=0, rhs=0 ) )	

			# consider each resource selection
			for RA in T.resources_req :
				# sum up resource distribution for each resource selection
				for t in range(MAX_TIME) :
					affine = pl.LpAffineExpression([ (x[(T,R,t)],1) for R in RA ] + [(x[(T,t)],-1)])
					cons.append( pl.LpConstraint( affine, sense=0, rhs=0 ) )


			# TODO: has not perfectly tested
			# fix variables if start is given
			starts = [ T_.start for T_ in self.task_groups[T] if T_.start is not None ]
			if starts and max(starts) > self.horizon :
					raise Exception('ERROR: fixed start of task '+str(T)+' larger than max time step '+str(horizon))
			for t in starts : 
				starts_after_t = [ t_ for t_ in starts if t_ >= t ]
				cons.append( pl.LpConstraint( x[(T,t)], sense=1, rhs=len(starts_after_t) ) )

			# TODO: not perfectly tested
			# fix resources if they are given
			resources = [ R for T_ in self.task_groups[T] if T_.resources for R in T_.resources ]
			for R in T.resources_req.resources() :
				if R in resources :
					cons.append( pl.LpConstraint( pl.LpAffineExpression([ (x[(T,R,0)],1) ]), sense=1, rhs=resources.count(R) ) )
			



		# objective
		objective = S.objective() # TODO: mix task_groups with objective
		mip += pl.LpAffineExpression([ ( x[(T,t)], objective[T]) for T in set(objective) & set(self.task_groups) for t in range(MAX_TIME)  ] )

		# resource non-overlapping constraints 
		for R in S.resources() :
			for t in range(MAX_TIME-1) :
				resource_tasks = [ T for T in self.task_groups if R in T.resources_req.resources() ]
				affine = pl.LpAffineExpression([ (x[(T,R,max(t-T.length,0))], 1) for T in resource_tasks ] + \
                                                                 [ (x[(T,R,t)], -1) for T in resource_tasks ])
				con =  pl.LpConstraint( affine, sense=-1, rhs=1.0 )
				cons.append(con)
				#prob += sum([ x[(T,max(t-T.length,0))]-x[(T,t)] for T in resource_tasks ]) <= 1.0

			# TODO: check capacity for task_groups
			'''
			#if R.capacity :
			#	resource_tasks = [ T for T in task_groups if R in T.resources_req.resources() ]
			#	affine = pl.LpAffineExpression([ (x[T,R,0],T.resources_req.capacity(R)) for T in resource_tasks ])
			#	con =  pl.LpConstraint( affine, sense=-1, rhs=R.capacity )
			#	cons.append(con)
			'''

		# TODO: precedence constraints only count if defined on group identifiers
		# precedence constraints
		for P in S.precs_lax() :
			if P.left in self.task_groups and P.right in self.task_groups :
				left_size = float(len(self.task_groups[P.left]))
				right_size = float(len(self.task_groups[P.right]))
				for t in range(MAX_TIME) :
					affine = pl.LpAffineExpression([ ( x[(P.left,t)], 1/left_size), (x[(P.right,min(t+P.left.length+P.offset,MAX_TIME-1))],-1/right_size)  ])
					con = pl.LpConstraint( affine, sense=-1, rhs=0 )
					cons.append(con)
	
		# tight precedence constraints
		for P in S.precs_tight() :
			if P.left in self.task_groups and P.right in self.task_groups :
				left_size = float(len(self.task_groups[P.left]))
				right_size = float(len(self.task_groups[P.right]))
				for t in range(MAX_TIME) :
					affine = pl.LpAffineExpression([ ( x[(P.left,t)], 1/left_size), (x[(P.right,min(t+P.left.length,MAX_TIME-1))],-1/right_size)  ])
					con = pl.LpConstraint( affine, sense=0, rhs= -P.offset )
					cons.append(con)

		# conditional precedence constraints
		for P in S.precs_cond() :
			if P.left in self.task_groups and P.right in self.task_groups :
				left_size = float(len(self.task_groups[P.left]))
				right_size = float(len(self.task_groups[P.right]))
				shared_resources = list( set(P.left.resources_req.resources()) & set(P.right.resources_req.resources()) )
				for R in shared_resources :	
					for t in range(MAX_TIME) :
						affine = pl.LpAffineExpression([ ( x[(P.left,R,max(t-P.left.length,0) )],1 ), (x[(P.left,R,t)],-1),\
				                                                 ( x[(P.right,R,max(t-P.left.length,0))], 1), (x[(P.right,R,min(t+P.offset,MAX_TIME-1) )],-1) ])
						con = pl.LpConstraint( affine, sense=-1, rhs=1 )
						cons.append(con)

		# lower bounds
		for P in S.precs_low() :
			T_left = task_to_group[P.left]
			cons.append( x[(T_left,P.right)] == 1 )

		# upper bounds
		for P in S.precs_up() :
			T_left = task_to_group[P.left]
			cons.append( x[(T_left,P.right)] == 0 )

		for con in cons :
			mip.addConstraint(con)

		self.mip = mip
		self.x = x


	def read_solution_from_mip(self,msg=0) :

		for T in self.task_groups :
			starts = [ t for t in range(self.horizon-1) \
                                   for i in range( int( self.x[(T,t)].varValue-self.x[(T,t+1)].varValue ) ) ]

			RA_resources = collections.OrderedDict()
			for RA in T.resources_req :
				RA_resources[RA] = [ R for t in range(self.horizon-1) for R in RA \
                                   for i in range( int( self.x[(T,R,t)].varValue-self.x[(T,R,t+1)].varValue ) ) ]			

			# check for predefined starts
			for T_ in self.task_groups[T] :
				if T_.start is not None :
					starts.remove(T_.start)
				if T_.resources is not None :
					for R in T_.resources :
						for RA in T.resources_req :
							RA_resources[RA].remove(R)

			start_count = 0
			resource_count = 0		
			for T_ in self.task_groups[T] :
				if T_.start is None :
					T_.start = starts[start_count]
					start_count += 1
				if T_.resources is None :
					T_.resources = []
					for RA in T.resources_req :
						T_.resources.append(RA_resources[RA][resource_count])
					resource_count += 1






	def solve(self,scenario,horizon='100',kind='CBC',time_limit=None,task_groups=None,msg=0) :
		"""
		Solves the given scenario using a discrete MIP via the pulp package

		Args:
			scenario:            scenario to solve
			kind:                MIP-solver to use: CPLEX, GLPK, CBC
			horizon :     the number of time steps to model
			time_limit:         a time limit, only for CPLEX and CBC
			msg:                 0 means no feedback (default) during computation, 1 means feedback
	
		Returns:
			scenario is solving was successful
			None if solving was not successful
		"""

		self.scenario = scenario
		self.horizon = horizon
		self.task_groups = task_groups
		self.build_mip_from_scenario(msg=msg)
		_solve_mip(self.mip,kind=kind,time_limit=time_limit,msg=msg)

		if self.mip.status != 1 :
			if msg : print ('ERROR: no solution found')
			#return None #TODO: problem sometimes still returned 0 when solution found

		self.read_solution_from_mip(msg=msg)	
		return self.scenario ##TODO: check what to return
	









