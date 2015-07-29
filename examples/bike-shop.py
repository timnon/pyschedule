#! /usr/bin/python

'''
Alice and Bob are running a nice Paint Studio for bikes where they pimp bikes with the newest colors. Today they have to paint a green and a red bike. So what they do they create a scenario using pyschedule:
'''

import os
path = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(path+'/pics'):
	os.makedirs(path+'/pics')

import pyschedule
S = pyschedule.Scenario('bike paint shop')

Alice = S.Resource('Alice')
Bob = S.Resource('Bob')

green_pre = S.Task('green pre')
green_paint = S.Task('green paint',length=2)
green_post = S.Task('green post')

red_pre = S.Task('red pre')
red_paint = S.Task('red paint',length=2)
red_post = S.Task('red post')
# STEP 0 (init entities)

#S += green_pre + 1 <= green_paint
S += green_pre < green_paint, green_paint + 1 < green_post
S += red_pre <= red_paint, red_paint < red_post

'''
S += green_pre % Alice | Bob
S += green_paint % Alice | Bob
S += green_post % Alice | Bob

S += red_pre % Alice | Bob
S += red_paint % Alice | Bob
S += red_post % Alice | Bob
'''

S += Alice|Bob % {green_pre,green_paint,green_post}
S += Alice|Bob % {red_pre,red_paint,red_post}


task_colors = {red_pre: '#EB4845', red_paint:'#EB4845', red_post: '#EB4845', 
               green_pre: '#A1D372', green_paint: '#A1D372', green_post: '#A1D372'}

def run(img_filename,makespan=True) :
	print('INFO: compute picture:'+str(img_filename))
	import copy
	S_ = copy.deepcopy(S)
	if makespan :
		S_.use_makespan_objective()
	pyschedule.solvers.pulp.solve(S_,kind='CBC',msg=1)
	task_colors_ = { S_.T[str(T)] : task_colors[T] for T in task_colors }
	pyschedule.plotters.matplotlib.plot(S_,img_filename=path+img_filename,color_prec_groups=False,hide_tasks=['MakeSpan'],task_colors=task_colors_,fig_size=(15,6))
run(img_filename='/pics/bike-shop-first.png')
# STEP 1

Paint_Shop = S.Resource('Paint Shop')
S += red_paint % Paint_Shop
S += green_paint % Paint_Shop
run(img_filename='/pics/bike-shop-paint-shop.png')
# STEP 2 (added paint shop increases length by one

S += green_pre > 2
run(img_filename='/pics/bike-shop-later.png')
# STEP 3 (add release time)

S += red_paint + 3 << green_paint
run(img_filename='/pics/bike-shop-changeover.png')
# STEP 5 (add changeover cost)

lunch = S.Task('lunch')
S += lunch > 3, lunch < 5
S += lunch % {Alice, Bob}
task_colors[lunch] = '#7EA7D8'
run(img_filename='/pics/bike-shop-lunch.png')
# STEP 6 (add lunch)

S.objective.clear()
S += green_post*5 + red_post
run(img_filename='/pics/bike-shop-flow-time.png',makespan=False)
# STEP 7 (flow-time objective)















