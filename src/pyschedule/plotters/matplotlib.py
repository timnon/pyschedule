from __future__ import absolute_import as _absolute_import
import operator

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


def plot(scenario,img_filename=None,resource_height=1.0,show_task_labels=True,
         color_prec_groups=False,hide_tasks=[],hide_resources=[],task_colors=dict(),fig_size=(15,5),
		 vertical_text=False) :
	"""
	Plot the given solved scenario using matplotlib

	Args:
		scenario:    scenario to plot
		msg:         0 means no feedback (default) during computation, 1 means feedback
	"""
	try :
		import matplotlib.patches as patches, matplotlib.pyplot as plt
	except :
		raise Exception('ERROR: matplotlib is not installed')
	import random

	S = scenario
	# trivial connected components implementation to avoid
	# having to import other packages just for that
	def get_connected_components(edges) :
		comps = dict()
		for v,u in edges :
			if v not in comps and u not in comps :
				comps[v] = v
				comps[u] = v
			elif v in comps and u not in comps :
				comps[u] = comps[v]
			elif v not in comps and u in comps :
				comps[v] = comps[u]
			elif v in comps and u in comps and comps[v] != comps[u] :
				old_comp = comps[u]
				for w in comps :
					if comps[w] == old_comp :
						comps[w] = comps[v]
		# replace component identifiers by integers startting with 0
		values = list(comps.values())
		comps = { T : values.index(comps[T]) for T in comps }
		return comps

	tasks = [ T for T in S.tasks() if T not in hide_tasks ]

	# get connected components dict for coloring
	# each task is mapping to an integer number which corresponds
	# to its connected component
	edges = [ (T,T) for T in tasks ]
	if color_prec_groups :
		edges += [ (T,T_) for P in set(S.precs_lax()) | set(S.precs_tight()) \
	                   for T in P.tasks() for T_ in P.tasks() \
                           if T in tasks and T_ in tasks ]
	comps = get_connected_components(edges)

	# color map
	colors = ['#7EA7D8','#A1D372','#EB4845','#7BCDC8','#FFF79A'] #pastel colors
	#colors = ['red','green','blue','yellow','orange','black','purple'] #basic colors
	colors += [ [ random.random() for i in range(3) ] for x in range(len(S.tasks())) ] #random colors
	color_map = { T : colors[comps[T]] for T in comps }
	# replace colors with fixed task colors

	for T in task_colors :
		color_map[T] = task_colors[T]
	hide_tasks_str = [ T for T in hide_tasks ]
	for T in scenario.tasks():
		if hasattr(T,'plot_color'):
			if T['plot_color'] is not None:
				color_map[T] = T['plot_color']
			else:
				hide_tasks_str.append(T)

	solution = S.solution()
	solution = [ (T,R,x,y) for (T,R,x,y) in solution if T not in hide_tasks_str ] #tasks of zero length are not plotted

	fig, ax = plt.subplots(1, 1, figsize=fig_size)
	resource_sizes_count = 0
	visible_resources = [ R for R in S.resources() if R not in hide_resources ]
	if not visible_resources:
		raise Exception('ERROR: no resources to plot')
	total_resource_sizes = sum([ R.size for R in visible_resources ])
	R_ticks = list()

	for R in visible_resources :
		if R.size is not None :
			resource_size = R.size
		else :
			resource_size = 1.0
		R_ticks += [str(R.name)]*int(resource_size)
		# compute the levels of the tasks on one resource
		task_levels = dict()
		# get solution on resource sorted according to start time
		R_solution = [ (T,R_,x,y) for (T,R_,x,y) in solution if R_ == R ]
		R_solution = sorted(R_solution, key=lambda x : x[2])
		# iteratively fill all levels on resource, start with empty fill
		level_fill = { i : 0 for i in range(int(resource_size)) }
		for T,R_,x,y in R_solution :
			sorted_levels =  sorted(level_fill.items(), key = operator.itemgetter(1, 0))
			# get the maximum resource requirement
			coeff = max([ RA[R] for RA in T.resources_req if R_ in RA ])
			min_levels = [ level for level,fill in sorted_levels[:coeff] ]
			task_levels[T] = min_levels
			for level in min_levels :
				level_fill[level] += T.length
		# plot solution
		for (T,R,x,x_) in R_solution :
			for level in task_levels[T] :
				y = (total_resource_sizes-1-(resource_sizes_count+level))*resource_height
				ax.add_patch(
				    patches.Rectangle(
					(x, y),       # (x,y)
					max(x_-x,0.5),   # width
					resource_height,   # height
					color = color_map[T],
					alpha=0.6
				    )
				)
				if show_task_labels :
					if vertical_text:
						text_rotation = 90
						y_ = y+0.9*resource_height
					else:
						text_rotation = 0
						y_ = y+0.1*resource_height
					plt.text(x,y_,str(T.name),fontsize=14,color='black',rotation=text_rotation)
		resource_sizes_count += resource_size

	# format graph
	plt.title(str(S.name))
	plt.yticks([ resource_height*x + resource_height/2.0 for x in range(len(R_ticks)) ],R_ticks[::-1])
	plt.ylim(0,resource_sizes_count*resource_height)#resource_height*len(resources))
	plt.xlim(0,max([ x_ for (I,R,x,x_) in solution if R in visible_resources ]))
	if img_filename :
		fig.figsize=(1,1)
		plt.savefig(img_filename,dpi=200,bbox_inches='tight')
	else :
		plt.show()
