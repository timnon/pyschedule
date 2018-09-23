#! /usr/bin/env python
import sys
sys.path.append('../src')
import getopt
opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
from pyschedule import Scenario, solvers, plotters

horizon = 10
S = Scenario('Scenario',horizon=horizon)
tasks = S.Tasks('T',num=int(horizon/2),is_group=True,completion_time_cost=2,state=1)
breaks = S.Tasks('B',num=int(horizon/2),is_group=True,completion_time_cost=1,state=-1)

R = S.Resource('R')
tasks += R
breaks += R

# ensure that state is always between 0 and 1
for t in range(horizon):
	S += R['state'][:t] <= 1
	S += R['state'][:t] >= 0

if solvers.mip.solve(S, msg=0):
	if ('--test','') in opts:
		assert( list(set([ T.start_value % 2 for T in tasks ]))[0] == 0 )
		assert( list(set([ T.start_value % 2 for T in breaks ]))[0] == 1 )
		print('test passed')
	else:
		plotters.matplotlib.plot(S, fig_size=(10, 5))
else:
	print('no solution found')
	assert(1==0)
