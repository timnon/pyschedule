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

import time, os, uuid


def get_tmp_dir() :
        """
	returns a default temporary directory
	"""
	if os.name != 'nt':
		# On unix use /tmp by default
		tmp_dir = os.environ.get("TMPDIR", "/tmp")
		tmp_dir = os.environ.get("TMP", tmp_dir)
	else:
		# On Windows use the current directory
		tmp_dir = os.environ.get("TMPDIR", "")
		tmp_dir = os.environ.get("TMP", tmp_dir)
		tmp_dir = os.environ.get("TEMP", tmp_dir)
	if not os.path.isdir(tmp_dir):
		tmp_dir = ""
	elif not os.access(tmp_dir, os.F_OK + os.W_OK):
		tmp_dif = ""
	return tmp_dir


def _create_files(scenario,mod_filename_master=None,msg=0) :

	S = scenario
	solvers_path = os.path.dirname(os.path.realpath(__file__))
	tmp_dir = get_tmp_dir()
	
	unique_suffix = uuid.uuid4()
	mod_filename = tmp_dir+'/pyschedule_'+str(unique_suffix)+'.mod'
	dat_filename = tmp_dir+'/pyschedule_'+str(unique_suffix)+'.dat'
	out_filename = tmp_dir+'/pyschedule_'+str(unique_suffix)+'.out'

	# get default master .mod file
	if mod_filename_master is None :
		mod_filename_master = solvers_path+'/cpoptimizer.mod'
		
	# create temporary .mod file with path to out-file
	model = open(mod_filename_master).read().replace('##out_filename##','"'+out_filename+'"')
	f = open(mod_filename,'w')
	f.write(model)
	f.close()

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
					TaskResources.append( (task_id,resource_id,T.length,task_resource_group_id) )
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

	# write .dat-file
	f = open(dat_filename,'w')
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

	# TODO: use real task and resource names in .mod-file
	return mod_filename, dat_filename, out_filename, task_to_id, id_to_resource



def _read_solution(scenario,log,task_to_id,id_to_resource) :
	
	S = scenario

	# parse output 
	from pyparsing import Keyword,Literal,Word,alphas,nums,printables,OneOrMore,ZeroOrMore,dblQuotedString,Group
	INT = Word( nums )
	int_row = Group( INT + INT +\
                         Literal("<").suppress() + \
	                 INT + INT + INT + INT + \
                         Literal(">").suppress() )
	'''
	plan = Group( Keyword("##START_INTERVALS##").suppress() + \
                      Group( ZeroOrMore(int_row) ) + \
                      Keyword("##END_INTERVALS##").suppress() )
	'''
	plan = Group( Group( ZeroOrMore(int_row) ) )

	#opl_plan = plan.parseFile(out_filename)
	start_str, end_str = '##START_INTERVALS##', '##END_INTERVALS##'
	start_i, end_i = log.index(start_str)+len(start_str), log.index(end_str)
	opl_plan = plan.parseString(log[start_i:end_i])
	int_plan = opl_plan[0][0]

	# get starts and resource assignments
	starts = dict()
	assign = dict()
	for row in int_plan :
		if int(row[2]) : # is interval active
			task_id = int(row[0])
			starts[task_id] = int(row[3])
			if task_id not in assign :
				assign[task_id] = list()
			assign[task_id].append(int(row[1]))

	# add to scenario
	for T in S.tasks() :
		T.start = starts[task_to_id[T]] #second column is start
		if T.resources is None :
			T.resources = list()
		T.resources += [ id_to_resource[j] for j in assign[task_to_id[T]] ]
	


def solve(scenario,mod_filename_master=None,msg=0) :
	""" solve using cpoptimzer, make sure that the executable oplrun is in your PATH """

	S = scenario
	mod_filename, dat_filename, out_filename, task_to_id, id_to_resource = _create_files(scenario,mod_filename_master,msg=msg)

	# run cp-optimizer
	start_time = time.time()
	#os.system('oplrun '+mod_filename+' '+dat_filename)
	log = os.popen('oplrun '+mod_filename+' '+dat_filename).read()
	if msg : print('INFO: execution time (sec) = '+str(time.time()-start_time))

	# read solution
	_read_solution(S,log,task_to_id,id_to_resource)
	if msg : print('INFO: finished reading solution')



def solve_docloud(scenario,api_key,base_url='https://api-oaas.docloud.ibmcloud.com/job_manager/rest/v1/',mod_filename_master=None,msg=0) :
	""" solve using DOCloud, api_key is required """
	from docloud import DOcloud
	S = scenario
	mod_filename, dat_filename, out_filename, task_to_id, id_to_resource = _create_files(scenario,mod_filename_master,msg=msg)
	doc = DOcloud(base_url, api_key, verbose=msg)
	log = doc.solve(filenames=[mod_filename,dat_filename])
	_read_solution(S,log,task_to_id,id_to_resource)








