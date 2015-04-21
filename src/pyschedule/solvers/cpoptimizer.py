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

#TODO: add capacity constraints (with numbers)
#TODO: add alternative resources

def solve(scenario,msg=0) :

	S = scenario
	solvers_path = os.path.dirname(os.path.realpath(__file__))
		
	# no objective specified
	if not S.objective :
		S.use_makespan_objective()

	# check if there are alternative resources
	if max([ len(RA) for T in S.tasks() for RA in T.resources_req ]) > 1 :
		raise Exception('ERROR: alternative resources not supported yet for CP-optimizer')

	resources = S.resources()
	tasks = S.tasks()
	precedences = S.precs_lax()

	id_to_resource = dict(zip(range(len(resources)),resources))
	resource_to_id = dict(zip(resources,range(len(resources))))

	id_to_task = dict(zip(range(len(tasks)),tasks))
	task_to_id = dict(zip(tasks,range(len(tasks))))

	Resources = [ (resource_to_id[R],R.capacity) for R in resources if R.capacity != None ]
	Resources += [ (resource_to_id[R],1000) for R in resources if R.capacity == None ] #TODO: remove 100
	Resources = sorted(Resources)

	# Tasks for .dat-file
	Tasks = list()
	TaskResources = list()
	for T in tasks :				
		Tasks.append( (task_to_id[T],int(T.length)) )
		for RA in T.resources_req :
			if len(RA) != 1 :
				raise Exception('ERROR: opl can only deal with single resource reqs')
			for R in RA :
				TaskResources.append( (task_to_id[T],resource_to_id[R]) )
					
	Tasks = sorted(Tasks)
	TaskResources = sorted(TaskResources)

	# Precedences for .dat-file
	Precedences = list()
	for P in S.precs_lax() :
		Precedences.append(( task_to_id[P.left],task_to_id[P.right],P.offset))

	TightPrecedences = list()
	for P in S.precs_tight() :
		Precedences.append(( task_to_id[P.left],task_to_id[P.right],P.offset))

	CondPrecedences = list()
	for P in S.precs_cond() :
		CondPrecedences.append(( task_to_id[P.left],task_to_id[P.right],P.offset))

	LowerBounds = list()
	for P in S.precs_up() :
		UpperBounds.append((task_to_id[P.left],offset))

	UpperBounds = list()
	for P in S.precs_low() :
		LowerBounds.append((task_to_id[P.right],-offset))

	# TODO: support all other precedences. Support also tight upper and lower bounds

	Precedences = sorted(Precedences)
	CondPrecedences = sorted(CondPrecedences)

	# add objective
	Objectives = list()
	for key in S.objective :
		Objectives.append( (task_to_id[key],S.objective[key]) )
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
	f.write('TaskResources={\n'+to_str(TaskResources)+'\n};\n\n')
	f.write('Precedences={\n'+to_str(Precedences)+'\n};\n\n')
	f.write('TightPrecedences={\n'+to_str(TightPrecedences)+'\n};\n\n')
	f.write('CondPrecedences={\n'+to_str(CondPrecedences)+'\n};\n\n')
	f.write('UpperBounds={\n'+to_str(UpperBounds)+'\n};\n\n')
	f.write('LowerBounds={\n'+to_str(LowerBounds)+'\n};\n\n')
	f.close()

	# run cp-optimizer
	start_time = time.time()
	os.system('oplrun '+solvers_path+'/cpoptimizer.mod '+solvers_path+'/tmp/cpoptimizer.dat')
	if msg : print('INFO: execution time (sec) = '+str(time.time()-start_time))

	# parse output 
	from pyparsing import Literal,Word,alphas,nums,printables,OneOrMore,ZeroOrMore,dblQuotedString,Group
	
	INT = Word( nums )

	int_row = Group( Literal("<").suppress() + \
	                    INT + INT + INT + INT + \
                            Literal(">").suppress() )

	res_seq_row = Group( Literal("<").suppress()  + dblQuotedString + \
	                    INT + INT + INT + \
	                    INT + INT + INT + \
                            Literal(">").suppress() )
	res_seq = Group( Literal("{").suppress() + ZeroOrMore(res_seq_row) + Literal("}").suppress() )

	plan = Group(ZeroOrMore(int_row)) + Group(ZeroOrMore(res_seq))

	opl_plan = plan.parseFile(solvers_path+'/tmp/cpoptimizer.out')

	int_plan = opl_plan[0]
	res_seq_plan = opl_plan[1]

	# get starts of tasks
	starts = { i : int(int_plan[i][1]) for i in range(len(int_plan)) }

	assign = { int(row[2]) : id_to_resource[i] for i in range(len(res_seq_plan)) \
                                  for row in res_seq_plan[i] if int(row[4]) == starts[int(row[2])] }

	# add to scenario
	for T in S.tasks() :
		T.start = starts[task_to_id[T]] #second column is start
		T.resources = [assign[task_to_id[T]]] #assume only one resource






