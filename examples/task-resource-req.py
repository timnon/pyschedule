# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path.append('../src')
import getopt
opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])

horizon=10

from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('shift_bounds',horizon=horizon)

# define two employees
R = S.Resources('R',num=2)

T0 = S.Task('T0',completion_time_cost=3)
T0 += alt(R)

T1 = S.Task('T1',completion_time_cost=1)
T1 += alt(R)

T1 += T0*R[0]
T0 += T1*R[0]

if solvers.mip.solve(S, msg=0):
	if ('--test','') in opts:
		assert(T0.start_value == 0)
		assert(T1.start_value == 1)
		print('test passed')
	else:
		plotters.matplotlib.plot(S, fig_size=(10, 5), vertical_text=True)
else:
	print('no solution found')
	assert(1==0)
