
import sys
sys.path += ['../src','src']
import getopt
opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
from pyschedule import Scenario, solvers, plotters

horizon = 20
S = Scenario('switch',horizon=horizon)
# Set some colors for the tasks
task_colors = dict()
task_group_colors = { 'A': 'green', 'B': 'red', 'C':'blue'}

R_machine = S.Resource('machine')
T = dict()

task_types = { 'A': 1, 'B': 2, 'C': 3}
task_lengths = { 'A': 2, 'B': 3, 'C':1 }

max_n_switches = 10
for i in range(max_n_switches):
	name = 'S_%i'%i
	T[name] = S.Task(name,group='switch')
	T[name] += R_machine
	T[name]['schedule_cost'] = 0.001
	for task_type in task_types:
		setup_param = '%s_state'%task_type
		T[name][setup_param] = 1

for task_type in task_types:
	for i in range(task_types[task_type]):
		name = '%s_%i'%(task_type,i)
		setup_param = '%s_state'%task_type
		T[name] = S.Task(name,group=task_type,length=task_lengths[task_type])
		T[name][setup_param] = 2
		#T[name]['reward'] = 1
		T[name] += R_machine
		task_colors[T[name]] = task_group_colors[task_type]

for task_type in task_types:
	for t in range(horizon-1):
		setup_param = '%s_state'%task_type
		C = R_machine[setup_param][t:t+2].inc <= 1
		S += C

S.use_flowtime_objective()
if solvers.mip.solve(S,msg=0,kind='CBC'):
	if ('--test','') in opts:
		assert( S['S_0'].start_value == 3 )
		assert( S['S_1'].start_value == 6 )
		print('test passed')
	else:
		plotters.matplotlib.plot(S,task_colors=task_colors)
else:
	print('no solution found')
	assert(1==0)
