#! /usr/bin/env python
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

"""
This module contains solvers that accept the pyschedule scenario format
as input. Each solver should correspond to a class which offers the
method "solve" that takes a scenario as minimal input. If a solution
exists, then a 0 should be returned, otherwise a 1. The optimal solution
should be directly written to the passed scenario
"""

from pyschedule import *
import time


# asdfdsfsdffdasfdfsdfdsfdfadsf
class pulp(object) :
	"""
	An interface to the pulp MIP solver package, supported are CPLEX and GLPK
	"""

	def __init__(self) :
		pass

	def solve(self,scenario,kind='CPLEX',msg=0,lp_filename=None) :
		"""
		Solves the given scenario using a MIP via package pulp, the solution will
		be written to the given scenario

		Args:
			scenario:    scenario to solve
			kind:        MIP-solver to use: CPLEX, GLPK
			msg:         0 means no feedback (default) during computation, 1 means feedback
			lp_filename: if set, then a .lp file will be written here
	
		Returns:
			0: good
			1: no solution exists
		"""

		self.scenario=scenario
		S = scenario

		import pulp
		start_time = time.time()

		T_MAX = 10000 #TODO: GLPK has problems with large number
		prob = pulp.LpProblem(S.name, pulp.LpMinimize)

		# all task variables
		x = dict()
		for T in S.tasks :
			x[str(T)] = pulp.LpVariable(T,0)
			# add assignment variable for each  tresource
			for R in T.resource_req.resources() :
				x[(str(T),str(R))] = pulp.LpVariable((T,R),0,1,cat=pulp.LpInteger)

		# generate objective
		if not S.objective :
			if msg : print('INFO: use makespan objective as default')
			makespan = pulp.LpVariable('obj',0)
			prob += makespan, 'obj'
			# constraint makespan
			for T in S.tasks :
				prob += x[str(T)] + T.length <= makespan
		else :
			prob += sum([ x[str(T)]*S.objective[T] for T in S.objective if isinstance(T,Task) ])

		# everybody is required on one resource from each or clause
		for T in S.tasks :
			if T.resource_req :
				for RA in T.resource_req :
					if RA :
						x[(str(T),str(RA),'RA')] = pulp.LpVariable((T,RA,'RA'),0,1,cat=pulp.LpInteger)
						prob += x[(str(T),str(RA),'RA')] <= \
						        sum([ x[(str(T),str(R))] for R in RA ]) * (1/float(len(RA)))
				prob += sum([ x[(str(T),str(RA),'RA')] for RA in T.resource_req ]) >= 1
	
		# resource capacity constraints #TODO: add resource req weights
		for R in S.resources :
			if R.capacity :
				prob += sum([ x[(str(T),str(RA),'RA')]*RA[R] for T in S.tasks \
		                              for RA in T.resource_req if R in RA ]) <= R.capacity
				''' TODO: remove old constraint without capacities
				con2 = sum([ x[(str(T),str(R))] for T in S.tasks if R in T.resource_req.resources() ]) \
		                       <= R.capacity
				'''

		# generate a precedence contraint, optionally for a resource R
		def get_prec_cons(P,R=None) :
			cons = list()
			if P.kind == '<' :
				con = sum([ x[str(T)]*P[T]        for T in P if isinstance(T,Task) and P[T] <  0 ]) + \
		                      sum([ x[str(T)]*P[T]+T.length for T in P if isinstance(T,Task) and P[T] >= 0 ]) + \
		                      sum([      P[T]          for T in P if T == 1 ]) <= 0
				cons.append(con)
			elif P.kind == '<<' or P.kind == '!=' :
				z = pulp.LpVariable((P.left,P.right,R),0,1,cat=pulp.LpInteger)
				con1 = sum([ x[str(T)]*P[T]         for T in P if isinstance(T,Task) and P[T] <  0 ]) + \
		                      sum([ x[str(T)]*P[T]+T.length for T in P if isinstance(T,Task) and P[T] >= 0 ]) + \
		                      sum([      P[T]          for T in P if T == 1 ]) <= z*T_MAX
				con2 = sum([ -x[str(T)]*P[T]          for T in P if isinstance(T,Task) and P[T] >  0 ]) + \
		                      sum([  -x[str(T)]*P[T]+T.length for T in P if isinstance(T,Task) and P[T] <= 0 ]) <= (1-z)*T_MAX
				cons += [con1,con2]
			else :
				print('ERROR: precedence '+str(P)+' cant be interpreted')
				sys.exit()
			return cons

		# precedence constraints on scenario
		for P in S.precs :
			for con in get_prec_cons(P) :
				prob += con

		# precedence contraints on resources
		# relax to cases where both tasks are on same resource
		for R in S.resources :
			precs = R.precs

			# TODO: check this stuff
			# add != prec for assigned to same resource
			resource_tasks = { T for T in S.tasks if R in T.resource_req.resources() }
			
			# add resource conflict constraints
			K =  [ (T,T_) for T in resource_tasks for T_ in resource_tasks if T != T_ and str(T) > str(T_) ]
			for (T,T_) in K :
				precs.add( Precedence(TaskAffine(T),'!=',TaskAffine(T_)) )
		
			# generate for each precedence some contraints but make them only tight if
			# tasks are assigned to the same resource
			for P in precs :
				cons = get_prec_cons(P,R)
				for con in cons :
					for T in P.tasks() :
						con -= (1-x[(str(T),str(R))])*T_MAX #is added to the left side
					prob += con

		# write lp as file if requested
		if lp_filename : prob.writeLP(lp_filename)

		self.prob = prob
		time_limit = 4
		# select solver for pulp
		if kind == 'CPLEX' :
			prob.solve(pulp.CPLEX(msg=msg))
		elif kind == 'GLPK' :
			prob.solve(pulp.GLPK(msg=msg))
		else :
			raise Exception('ERROR: solver not known to pulp')

		if msg : print('INFO: execution time (sec) = '+str(time.time()-start_time))
		
		# if solving was succesful
		if prob.status == 1 :
			if msg : print('INFO: objective = '+str(pulp.value(prob.objective)))
			for T in S.tasks :
				T.start = x[str(T)].varValue
				T.actual_resources = [ R for R in T.resource_req.resources() if x[(str(T),str(R))].varValue > 0 ]
		else :
			if msg : print ('ERROR: no solution found')
			return 1


		return 0
	










