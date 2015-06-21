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

import time, os

def solve(scenario,msg=0) :

	S = scenario
	solvers_path = os.path.dirname(os.path.realpath(__file__))

	resources = S.resources()
	tasks = S.tasks()

	id_to_resource = dict(zip(range(len(resources)),resources))
	resource_to_id = dict(zip(resources,range(len(resources))))

	id_to_task = dict(zip(range(len(tasks)),tasks))
	task_to_id = dict(zip(tasks,range(len(tasks))))

	LARGE_NUMBER = 1000

	# TODO: only upper capacity constraints
	Resources = [ (resource_to_id[R],R.capacity[0],R.capacity[1]) for R in resources \
                      if R.capacity != None and R.size == 1 ]
	Resources += [ (resource_to_id[R],0,LARGE_NUMBER) for R in resources \
                      if R.capacity == None and R.size == 1 ]
	Resources = sorted(Resources)

	PulseResources = [ (resource_to_id[R],R.size) for R in resources \
                           if  R.size > 1 ]

	# Tasks for .dat-file
	Tasks = list()
	TaskResources = list()
	TaskResourceGroups = list()
	TaskPulsResources = list()
	for T in tasks :				
		Tasks.append( (task_to_id[T],int(T.length)) )
		for RA in T.resources_req :
			for R in RA :
				task_id = task_to_id[T]
				resource_id = resource_to_id[R]
				if R.size == 1 :
					task_resource_group_id = T.resources_req.index(RA)
					TaskResources.append( (task_id,resource_id,task_resource_group_id) )
					if (task_id,task_resource_group_id) not in TaskResourceGroups :
						TaskResourceGroups.append((task_id,task_resource_group_id))
				else :
					TaskPulsResources.append( (task_id,resource_id,T[R]) )
					if T.resources is None :
						T.resources = list()
					T.resources.append(R)

		if T.resources is not None :
			pass
			#TODO: accept fixed resources					
	
	Tasks = sorted(Tasks)
	TaskResources = sorted(TaskResources)
	TaskResourceGroups = sorted(TaskResourceGroups)

	# Precedences for .dat-file
	Precedences = list()
	for P in S.precs_lax() :
		Precedences.append(( task_to_id[P.left],task_to_id[P.right],P.offset))

	TightPrecedences = list()
	for P in S.precs_tight() :
		TightPrecedences.append(( task_to_id[P.left],task_to_id[P.right],P.offset))

	CondPrecedences = list()
	for P in S.precs_cond() :
		CondPrecedences.append(( task_to_id[P.left],task_to_id[P.right],P.offset))

	LowerBounds = list()
	for P in S.precs_low() :
		LowerBounds.append((task_to_id[P.left],P.right))

	UpperBounds = list()
	for P in S.precs_up() :
		UpperBounds.append((task_to_id[P.left],P.right))

	FixBounds = list()
	for T in S.tasks() :
		if T.start is not None :
			FixBounds.append((task_to_id[T],T.start))

	Precedences = sorted(Precedences)
	CondPrecedences = sorted(CondPrecedences)

	# add objective
	Objectives = [ (task_to_id[key],S.objective[key])  for key in S.objective if key != 1 ]
	#for key in S.objective :
	#	Objectives.append( (task_to_id[key],S.objective[key]) )
	Objectives = sorted(Objectives)

	# function to convert table into opl type typle lists
	def to_str(l) :
		return '\n'.join([ '<'+' '.join([ str(x) for x in row ])+'>'  \
                                  for row in l ])

	if not os.path.exists(solvers_path+'/tmp') :
		os.makedirs(solvers_path+'/tmp')

	# write .dat-file
	f = open(solvers_path+'/tmp/cpoptimizer.dat','w')
	f.write('Objectives={\n'+to_str(Objectives)+'\n};\n\n')
	f.write('Tasks={\n'+to_str(Tasks)+'\n};\n\n')
	f.write('Resources={\n'+to_str(Resources)+'\n};\n\n')
	f.write('PulseResources={\n'+to_str(PulseResources)+'\n};\n\n')
	f.write('TaskResources={\n'+to_str(TaskResources)+'\n};\n\n')
	f.write('TaskResourceGroups={\n'+to_str(TaskResourceGroups)+'\n};\n\n')
	f.write('TaskPulseResources={\n'+to_str(TaskPulsResources)+'\n};\n\n')
	f.write('Precedences={\n'+to_str(Precedences)+'\n};\n\n')
	f.write('TightPrecedences={\n'+to_str(TightPrecedences)+'\n};\n\n')
	f.write('CondPrecedences={\n'+to_str(CondPrecedences)+'\n};\n\n')
	f.write('UpperBounds={\n'+to_str(UpperBounds)+'\n};\n\n')
	f.write('LowerBounds={\n'+to_str(LowerBounds)+'\n};\n\n')
	f.write('FixBounds={\n'+to_str(FixBounds)+'\n};\n\n')
	f.close()

	# run cp-optimizer
	start_time = time.time()
	os.system('oplrun '+solvers_path+'/cpoptimizer.mod '+solvers_path+'/tmp/cpoptimizer.dat')
	if msg : print('INFO: execution time (sec) = '+str(time.time()-start_time))

	# parse output 
	from pyparsing import Keyword,Literal,Word,alphas,nums,printables,OneOrMore,ZeroOrMore,dblQuotedString,Group
	
	INT = Word( nums )

	int_row = Group( INT + \
                         Literal("<").suppress() + \
	                 INT + INT + INT + INT + \
                         Literal(">").suppress() )

	rint_row = Group( INT + INT +\
                         Literal("<").suppress() + \
	                 INT + INT + INT + INT + \
                         Literal(">").suppress() )

	res_seq_row = Group(Literal("<").suppress()  + dblQuotedString + \
	                    INT + INT + INT + \
	                    INT + INT + INT + \
                            Literal(">").suppress() )

	plan = Group( Keyword("INTERVALS").suppress() + Group( ZeroOrMore(int_row) ) +
                      Keyword("RINTERVALS").suppress() + Group( ZeroOrMore(rint_row) ) )#+

	opl_plan = plan.parseFile(solvers_path+'/tmp/cpoptimizer.out')

	int_plan = opl_plan[0][0]
	rint_plan = opl_plan[0][1]
	#res_seq_plan = opl_plan[0][2][0]

	# get starts of tasks #TODO: merge with resource assignment
	starts = { i : int(int_plan[i][2]) for i in range(len(int_plan)) }

	# get resource assignment
	assign = { i : [ int(rint_plan[j][1]) for j in range(len(rint_plan)) \
                         if int(rint_plan[j][0]) == i and int(rint_plan[j][2]) ] \
                         for i in starts.keys() }

	# add to scenario
	for T in S.tasks() :
		T.start = starts[task_to_id[T]] #second column is start
		if T.resources is None :
			T.resources = list()
		T.resources += [ id_to_resource[j] for j in assign[task_to_id[T]] ]








