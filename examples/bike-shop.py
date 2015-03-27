#! /usr/bin/env python

'''
Alice and Bob are running a nice Paint Studio for bikes where they pimp bikes with the newest colors. Today they have to paint a blue and a red bike. So what they do they create a scenario using pyschedule:
'''

from pyschedule import *
S = pyschedule.Scenario('bike paint shop')

Alice = S.Resource('Alice')
Bob = S.Resource('Bob')

blue_pre = S.Task('blue pre')
blue_paint = S.Task('blue paint',length=2)
blue_post = S.Task('blue post')

red_pre = S.Task('red pre')
red_paint = S.Task('red paint',length=2)
red_post = S.Task('red post')
# STEP 0 (init entities)

S += blue_pre < blue_paint, blue_paint < blue_post
S += red_pre < red_paint, red_paint < red_post

blue_pre += Alice | Bob
blue_paint += Alice | Bob
blue_post += Alice | Bob

red_pre += Alice | Bob
red_paint += Alice | Bob
red_post += Alice | Bob

def run(img_filename) :
	solvers.pulp().solve(S,kind='CPLEX',msg=1,lp_filename=None)
	plotters.gantt_matplotlib().plot(S,img_filename=img_filename,color_prec_groups=True,hide_tasks=[MakeSpan],task_colors={red_paint:'#EB4845',blue_paint:'#7EA7D8',lunch:'#A1D372'})
run()
# STEP 1

Paint_Shop = S.Resource('Paint Shop')
red_paint += Paint_Shop
blue_paint += Paint_Shop
# STEP 2 (added paint shop increases length by one

S += blue_pre > 2
# STEP 3 (add release time)

Paint_Shop += red_paint + 3 << blue_paint
# STEP 5 (add changeover cost)

lunch = S.Task('lunch')
S += lunch > 3, lunch < 5
lunch += Alice + Bob
# STEP 6 (add lunch)

MakeSpan = S.Task('MakeSpan')
S += MakeSpan > {blue_post,red_post}
S += MakeSpan
# STEP 6 (exchange objective)

S.objective.clear()
S += blue_post*5 + red_post
# STEP 7 (flow-time objective)



solvers.pulp().solve(S,kind='CPLEX',msg=1,lp_filename=None)
plotters.gantt_matplotlib().plot(S,color_prec_groups=True,hide_tasks=[MakeSpan],task_colors={red_paint:'#EB4845',blue_paint:'#7EA7D8',lunch:'#A1D372'})

print(S.__repr__())















