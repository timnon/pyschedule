#! /usr/bin/env python

'''
Alice and Bob are running a nice Paint Studio for bikes where they pimp bikes with the newest colors. Today they have to paint a green and a red bike. So what they do they create a scenario using pyschedule:
'''

import os
path = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(path+'/pics'):
	os.makedirs(path+'/pics')

from pyschedule import *
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


green_pre += Alice | Bob
green_paint += Alice | Bob
green_post += Alice | Bob

red_pre += Alice | Bob
red_paint += Alice | Bob
red_post += Alice | Bob

task_colors = {red_pre: '#EB4845', red_paint:'#EB4845', red_post: '#EB4845', 
               green_pre: '#A1D372', green_paint: '#A1D372', green_post: '#A1D372'}

def run(img_filename) :
	print('INFO: compute picture:'+str(img_filename))
	import copy
	S_ = copy.deepcopy(S)
	solvers.pulp.solve(S_,kind='CBC',msg=1)
	plotters.matplotlib.plot(S_,img_filename=path+img_filename,color_prec_groups=False,hide_tasks=['MakeSpan'],task_colors=task_colors,fig_size=(15,6))
run(img_filename='/pics/bike-shop-first.png')
# STEP 1

Paint_Shop = S.Resource('Paint Shop')
red_paint += Paint_Shop
green_paint += Paint_Shop
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
lunch += Alice + Bob
task_colors[lunch] = '#7EA7D8'
run(img_filename='/pics/bike-shop-lunch.png')
# STEP 6 (add lunch)

S.objective.clear()
S += green_post*5 + red_post
run(img_filename='/pics/bike-shop-flow-time.png')
# STEP 7 (flow-time objective)















