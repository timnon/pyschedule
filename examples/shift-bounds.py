# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path += ['../src','src']
import getopt
opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])

from pyschedule import Scenario, solvers, plotters, Task
S = Scenario('shift_bounds',horizon=8)

# define two employees
empl0 = S.Resource('empl0')
empl1 = S.Resource('empl1')

# employee 0 starts at two and ends
# at most four hours later
empl0_beg = S.Task('empl0_beg',delay_cost=2)
empl0_beg += empl0
empl0_fin = S.Task('empl0_fin',delay_cost=2)
empl0_fin += empl0
#S += 2 <= empl0_beg, empl0_fin < empl0_beg + 6

# employee 1 begins at any time and finishes
# at most four hours later
empl1_beg = S.Task('empl1_beg',delay_cost=2)
empl1_beg += empl1
empl1_fin = S.Task('empl1_fin',delay_cost=2)
empl1_fin += empl1
#S += empl1_fin < empl1_beg + 6

# interchangeable tasks that need to be finished as
# by the two employees as early as possible
T = S.Tasks(name='T',num=6,delay_cost=1,is_group=True)
T += empl0 | empl1

# bound tasks of employees by shift begin and finish
S += empl0_beg < T*empl0, T*empl0 < empl0_fin
S += empl1_beg < T*empl1, T*empl1 < empl1_fin


if solvers.mip.solve(S,msg=0,kind='CBC'):
	opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
	if ('--test','') in opts:
		assert(empl0_fin.start_value == 4)
		assert(empl1_fin.start_value == 4)
		print('test passed')
	else:
		plotters.matplotlib.plot(S)
else:
	print('no solution found')
	assert(1==0)
