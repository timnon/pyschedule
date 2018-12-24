# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path.append('../src')
horizon=4

import getopt
opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('test',horizon=horizon)

# define two employees
R = S.Resources('R',num=2)

T0 = S.Task('T0',length=2,delay_cost=4)
T0 += alt(R)

T1 = S.Task('T1',delay_cost=1)
T1 += R[0]

T2 = S.Task('T2',delay_cost=3)
T2 += alt(R)

S += T1 < T0*R[0]
S += T1 < T2*R[0]

#S += T1 < T0*R[0]
#S += T1 < T2*R[0]

if solvers.mip.solve(S, msg=0):
	opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
	if ('--test','') in opts:
		assert(T0.start_value == 0)
		assert(T1.start_value == 0)
		assert(T2.start_value == 1)
		print('test passed')
	else:
		plotters.matplotlib.plot(S, fig_size=(10, 5), vertical_text=True)
else:
	print('no solution found')
	assert(1==0)
