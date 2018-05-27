# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path.append('../src')

# working day with eight hours
from pyschedule import Scenario, solvers, plotters, Task
S = Scenario('shift_bounds',horizon=8)

# define two employees
empl0 = S.Resource('empl0')
empl1 = S.Resource('empl1')

# employee 0 starts at two and ends
# at most four hours later
empl0_beg = S.Task('empl0_beg',completion_time_cost=2)
empl0_beg += empl0
empl0_fin = S.Task('empl0_fin',completion_time_cost=2)
empl0_fin += empl0
S += 2 <= empl0_beg, empl0_fin < empl0_beg + 6

# employee 1 begins at any time and finishes
# at most four hours later
empl1_beg = S.Task('empl1_beg',completion_time_cost=2)
empl1_beg += empl1
empl1_fin = S.Task('empl1_fin',completion_time_cost=2)
empl1_fin += empl1
S += empl1_fin < empl1_beg + 6

# interchangeable tasks that need to be finished as
# by the two employees as early as possible
T = S.Tasks(name='T',n_tasks=6,is_group=True)
T *= empl0 | empl1

# bound tasks of employees by shift begin and finish
S += empl0_beg << T, T << empl0_fin
S += empl1_beg << T, T << empl1_fin

# alternatively, define each task separately
# and not as a interchangeable group
'''
T = dict()
for i in range(6):
	T[i] = S.Task('T%i'%i,completion_time_cost=1)
	T[i] += R1 | R2
	S += T[i] << T1_e, T1_s << T[i]
	S += T2_s << T[i], T[i] << T2_e
'''

if solvers.mip.solve(S,msg=1,kind='CBC'):
	plotters.matplotlib.plot(S)
else:
	print('no solution found')
