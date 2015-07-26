#! /usr/bin/env python
from __future__ import absolute_import
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


def _get_tmp_dir() :
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



def _get_dat_filename(scenario,msg=0) :

	S = scenario
	tmp_dir = _get_tmp_dir()
	unique_suffix = uuid.uuid4()
	dat_filename = tmp_dir+'/pyschedule_'+str(unique_suffix)+'.dat'

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

	CumulResources = [ (resource_to_id[R],R.size) for R in resources \
                           if  R.size > 1 ]

	# Tasks for .dat-file
	Tasks = list()
	TaskResources = list()
	TaskResourceGroups = list()
	TaskCumulResources = list()
	TaskTaskResources = list()
	for T in tasks :				
		Tasks.append( (task_to_id[T],int(T.length)) )

	# resource requirements
	for RA in S.resources_req() :
		tasks = RA.tasks()

		#TODO: allow fixed resources of different tasks
		it_resources = list(RA)
		# check if one of resources in RA is fixed
		for T in tasks :
			# check if one of resources in RA is fixed
			if T.resources is not None :
				fixed_resources = set(RA) & set(T.resources)
				if fixed_resources :
					it_resources = list(fixed_resources)[:1]
			for R in it_resources :
				task_id = task_to_id[T]
				resource_id = resource_to_id[R]
				if R.size == 1 :
					T_RAs = S.resources_req(task=T)
					task_resource_group_id = T_RAs.index(RA) #T.resources_req.index(RA)
					TaskResources.append( (task_id,resource_id,
										   T.length,task_resource_group_id) )
					if (task_id,task_resource_group_id) not in TaskResourceGroups :
						TaskResourceGroups.append((task_id,task_resource_group_id))
				else :
					TaskCumulResources.append( (task_id,resource_id,RA[R]) )

		# fixing similar tasks to resources
		T = tasks[0]
		for T_ in tasks[1:] :
			task_id_1 = task_to_id[T]
			task_id_2 = task_to_id[T_]
			for R in RA :
				resource_id = resource_to_id[R]
				TaskTaskResources.append((task_id_1,task_id_2,resource_id))

	Tasks = sorted(Tasks)
	TaskResources = sorted(TaskResources)
	TaskResourceGroups = sorted(TaskResourceGroups)
	TaskTaskResources = sorted(TaskTaskResources)

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
	Objectives = [ (task_to_id[key],S.objective[key]) for key in S.objective if key != 1 ]
	Objectives = sorted(Objectives)

	# function to convert table into opl type typle lists
	def to_str(l) :
		return '\n'.join([ '<'+' '.join([ str(x) for x in row ])+'>'  \
                                  for row in l ])

	# write .dat-file
	with open(dat_filename,'w') as f :
		f.write('Objectives={\n'+to_str(Objectives)+'\n};\n\n')
		f.write('Tasks={\n'+to_str(Tasks)+'\n};\n\n')
		f.write('Resources={\n'+to_str(Resources)+'\n};\n\n')
		f.write('CumulResources={\n'+to_str(CumulResources)+'\n};\n\n')
		f.write('TaskResources={\n'+to_str(TaskResources)+'\n};\n\n')
		f.write('TaskResourceGroups={\n'+to_str(TaskResourceGroups)+'\n};\n\n')
		f.write('TaskCumulResources={\n'+to_str(TaskCumulResources)+'\n};\n\n')
		f.write('TaskTaskResources={\n'+to_str(TaskTaskResources)+'\n};\n\n')
		f.write('Precedences={\n'+to_str(Precedences)+'\n};\n\n')
		f.write('TightPrecedences={\n'+to_str(TightPrecedences)+'\n};\n\n')
		f.write('CondPrecedences={\n'+to_str(CondPrecedences)+'\n};\n\n')
		f.write('UpperBounds={\n'+to_str(UpperBounds)+'\n};\n\n')
		f.write('LowerBounds={\n'+to_str(LowerBounds)+'\n};\n\n')
		f.write('FixBounds={\n'+to_str(FixBounds)+'\n};\n\n')
		f.close()

	return dat_filename, task_to_id, id_to_resource



def _read_solution(scenario,log,task_to_id,id_to_resource) :
	S = scenario

	# parse output 
	from pyparsing import Keyword,Literal,Word,alphas,nums,printables,OneOrMore,ZeroOrMore,dblQuotedString,Group
	INT = Word( nums )
	int_row = Group( INT + Literal(",").suppress() + \
                         INT + Literal(",").suppress() + \
			 INT + Literal(";").suppress() )
	plan = Group( Group( ZeroOrMore(int_row) ) )

	start_str, end_str = '##START_SOLUTION##', '##END_SOLUTION##'
	start_i, end_i = log.index(start_str)+len(start_str), log.index(end_str)
	opl_plan = plan.parseString(log[start_i:end_i])
	int_plan = opl_plan[0][0]

	# get starts and resource assignments
	starts = dict()
	assign = dict()
	for row in int_plan :
		task_id = int(row[0])
		starts[task_id] = int(row[2])
		if task_id not in assign :
			assign[task_id] = list()
		assign[task_id].append(int(row[1]))

	# add to scenario
	for T in S.tasks() :
		T.start = starts[task_to_id[T]]
		if T.resources is None :
			T.resources = list()
		T.resources = [ id_to_resource[j] for j in assign[task_to_id[T]] ]



def _get_mod_filename(mod_filename=None) :
	if mod_filename is None :
		solvers_path = os.path.dirname(os.path.realpath(__file__))
		return solvers_path+'/cpoptimizer.mod'
	return mod_filename



def solve(scenario,mod_filename=None,msg=0) :
	""" solve using cpoptimzer, make sure that the executable oplrun is in your PATH """
	S = scenario
	mod_filename = _get_mod_filename(mod_filename)
	dat_filename, task_to_id, id_to_resource = _get_dat_filename(scenario,msg=msg)

	# run cp-optimizer
	start_time = time.time()
	log = os.popen('oplrun %s %s' % (mod_filename, dat_filename) ).read()
	if msg : print('INFO: execution time (sec) = '+str(time.time()-start_time))

	# read solution
	_read_solution(S,log,task_to_id,id_to_resource)



def solve_docloud(scenario,api_key,
                  base_url='https://api-oaas.docloud.ibmcloud.com/job_manager/rest/v1/',
                  mod_filename=None,msg=0) :
	""" solve using DOCloud, api_key is required """
	S = scenario
	mod_filename = _get_mod_filename(mod_filename)
	dat_filename, task_to_id, id_to_resource = _get_dat_filename(scenario,msg=msg)

	# solve and read solution
	from . import docloud
	log = docloud.solve(base_url=base_url,api_key=api_key,filenames=[mod_filename,dat_filename],msg=msg)
	_read_solution(S,log,task_to_id,id_to_resource)





