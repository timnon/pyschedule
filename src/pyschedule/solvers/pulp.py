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

import time, copy
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


def solve_discrete(scenario,max_time_step,kind='CBC',time_limit=None,msg=0,return_copy=False) :
	"""
	Shortcut to discrete mip
	"""
	if return_copy :
		scenario = copy.deepcopy(scenario)
	DiscreteMIP().solve(scenario,max_time_step,kind=kind,time_limit=time_limit,msg=msg)
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


	def build_mip_from_scenario(self,msg=0) :

		S = self.scenario
		BIG_M = self.big_m #TODO: GLPK has problems with large number
		mip = pl.LpProblem(str(S), pl.LpMinimize)

		# check for objective
		if not S.objective :
			if msg : print('INFO: use makespan objective as default')
			S.use_makespan_objective()

		# task variables
		x = dict()
		for T in S.tasks() :
			x[T] = pl.LpVariable(T,0)

			# fix variables if start is given
			if T.start :
				mip += x[T] == T.start

			# add assignment variable for each possible resource
			for R in T.resources_req.resources() :
				x[(T,R)] = pl.LpVariable((T,R),0,1,cat=pl.LpBinary)

		# objective
		mip += sum([ x[T]*S.objective[T] for T in S.objective ])
		
		# everybody is required on one resource from each or clause
		for T in S.tasks() :
			for RA in T.resources_req :
				mip += sum([ x[(T,R)] for R in RA ]) >= 1

		# resource capacity constraints
		for R in S.resources() :
			if R.capacity :
				mip += sum([ x[(T,R)]*T.resources_req.capacity(R) for T in S.tasks() \
		                               if R in T.resources_req.resources() ]) <= R.capacity

		# same resource variable
		task_pairs = [ (T,T_) for T in S.tasks() for T_ in S.tasks() if str(T) < str(T_) ]
		for (T,T_) in task_pairs :
			shared_resources = list( set(T.resources_req.resources()) & set(T_.resources_req.resources()) )
			if shared_resources :
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
		for P in S.precs() :
			mip += x[P.left] + P.left.length + P.offset <= x[P.right] 
		
		# tight precedence constraints
		for P in S.precs_tight() :
			mip += x[P.left] + P.left.length + P.offset == x[P.right] 

		# conditional precedence constraints
		for P in S.precs_cond() :
			#T,T_ = tuple(sorted([P.left,P.right],key = lambda x : str(x) ))
			mip += x[P.left] + P.left.length + P.offset <= x[P.right] + \
	                        (1-x[(P.left,P.right)])*BIG_M + (1-x[(P.left,P.right,'SameResource')])*BIG_M

		# upper bounds
		for P in S.precs_up() :
			mip += x[P.left] + P.left.length <= P.right

		# lower bounds
		for P in S.precs_low() :
			mip += x[P.left] >= P.right

		self.mip = mip
		self.x = x


	def read_solution_from_mip(self,msg=0) :
		for T in self.scenario.tasks() :
			T.start = self.x[T].varValue
			T.resources = [ R for R in T.resources_req.resources() if self.x[(T,R)].varValue > 0 ]


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
		self.max_time_step = None
		self.mip = None
		self.x = None  # mip variables shortcut


	def build_mip_from_scenario(self,msg=0) :
		S = self.scenario
		MAX_TIME = self.max_time_step
		mip = pl.LpProblem(str(S), pl.LpMinimize)

		# check for objective
		if not S.objective :
			if msg : print('INFO: use makespan objective as default')
			S.use_makespan_objective()
		
		# task variables
		x = dict()
		cons = list()
		for T in S.tasks() :
			for t in range(MAX_TIME) :
				x[(T,t)] = pl.LpVariable((T,t),0,1)
			# lower boundary conditions
			cons.append( pl.LpConstraint( x[(T,0)], sense=0, rhs=1 ) )
			cons.append( pl.LpConstraint( x[(T,self.max_time_step-1)], sense=0, rhs=0 ) ) #required for no solution feedback
	
			# fix variables if start is given
			if T.start :
				if T.start > self.max_time_step :
					raise Exception('ERROR: fixed start of task '+str(T)+' larger than max time step '+str(max_time_step))
				cons.append( pl.LpConstraint( x[(T,T.start)], sense=0, rhs=1 ) )

			# generate variabels for task resources
			for R in T.resources_req.resources() :
				# variables
				for t in range(MAX_TIME) :
					x[(T,R,t)] = pl.LpVariable((T,R,t),0,1,cat=pl.LpBinary)

				# monotonicity
				for t in range(MAX_TIME-1) :
					cons.append( pl.LpConstraint( pl.LpAffineExpression([ (x[(T,R,t)],1), (x[(T,R,t+1)],-1) ]), sense=1, rhs=0 ) )

			# consider each resource selection
			for RA in T.resources_req :
				# sum up resource distribution for each resource selection
				for t in range(MAX_TIME) :
					affine = pl.LpAffineExpression([ (x[(T,R,t)],1) for R in RA ] + [(x[T,t],-1)])
					cons.append( pl.LpConstraint( affine, sense=0, rhs=0 ) )

		# objective
		mip += pl.LpAffineExpression([ ( x[(T,t)], S.objective[T]) for T in S.objective for t in range(MAX_TIME)  ] )

		# resource non-overlapping constraints 
		for R in S.resources() :
			for t in range(MAX_TIME-1) :
				resource_tasks = [ T for T in S.tasks() if R in T.resources_req.resources() ]
				affine = pl.LpAffineExpression([ (x[(T,R,max(t-T.length,0))], 1) for T in resource_tasks ] + \
                                                                 [ (x[(T,R,t)], -1) for T in resource_tasks ])
				con =  pl.LpConstraint( affine, sense=-1, rhs=1.0 )
				cons.append(con)
				#prob += sum([ x[(T,max(t-T.length,0))]-x[(T,t)] for T in resource_tasks ]) <= 1.0

			if R.capacity :
				resource_tasks = [ T for T in S.tasks() if R in T.resources_req.resources() ]
				affine = pl.LpAffineExpression([ (x[T,R,0],T.resources_req.capacity(R)) for T in resource_tasks ])
				con =  pl.LpConstraint( affine, sense=-1, rhs=R.capacity )
				cons.append(con)

		# precedence constraints
		for P in S.precs() :
			for t in range(MAX_TIME) :
				affine = pl.LpAffineExpression([ ( x[(P.left,t)], 1), (x[(P.right,min(t+P.left.length,MAX_TIME-1))],-1)  ])
				con = pl.LpConstraint( affine, sense=-1, rhs=0 )
				cons.append(con)

		# tight precedence constraints
		for P in S.precs_tight() :
			for t in range(MAX_TIME) :
				affine = pl.LpAffineExpression([ ( x[(P.left,t)], 1), (x[(P.right,min(t+P.left.length,MAX_TIME-1))],-1)  ])
				con = pl.LpConstraint( affine, sense=0, rhs=0 )
				cons.append(con)

		# conditional precedence constraints
		for P in S.precs_cond() :
			shared_resources = list( set(P.left.resources_req.resources()) & set(P.right.resources_req.resources()) )
			for R in shared_resources :	
				for t in range(MAX_TIME) :
					affine = pl.LpAffineExpression([ ( x[(P.left,R,max(t-P.left.length,0) )],1 ), (x[(P.left,R,t)],-1),\
		                                                          ( x[(P.right,R,max(t-P.left.length,0))], 1), (x[(P.right,R,min(t+P.offset,MAX_TIME-1) )],-1) ])
					con = pl.LpConstraint( affine, sense=-1, rhs=1 )
					cons.append(con)

		# lower bounds
		for P in S.precs_low() :
			cons.append( x[(P.left,P.right)] == 1 )

		# upper bounds
		for P in S.precs_up() :
			cons.append( x[(P.left,P.right)] == 0 )

		for con in cons :
			mip.addConstraint(con)

		self.mip = mip
		self.x = x


	def read_solution_from_mip(self,msg=0) :
		for T in self.scenario.tasks() :
			T.start = max([ t for t in range(self.max_time_step) if self.x[(T,t)].varValue == 1.0 ])
			T.resources = [ R for R in T.resources_req.resources() if self.x[(T,R,0)].varValue > 0 ]


	def solve(self,scenario,max_time_step='100',kind='CBC',time_limit=None,msg=0) :
		"""
		Solves the given scenario using a discrete MIP via the pulp package

		Args:
			scenario:            scenario to solve
			kind:                MIP-solver to use: CPLEX, GLPK, CBC
			max_time_step :     the number of time steps to model
			time_limit:         a time limit, only for CPLEX and CBC
			msg:                 0 means no feedback (default) during computation, 1 means feedback
	
		Returns:
			scenario is solving was successful
			None if solving was not successful
		"""
		self.scenario = scenario
		self.max_time_step = max_time_step
		self.build_mip_from_scenario(msg=msg)
		_solve_mip(self.mip,kind=kind,time_limit=time_limit,msg=msg)

		if self.mip.status != 1 :
			if msg : print ('ERROR: no solution found')
			return None
		self.read_solution_from_mip(msg=msg)	
		return self.scenario ##TODO: check what to return
	









