#! /usr/bin/python
import sys
sys.path.append('../src')
from pyschedule import Scenario, solvers, plotters

S = Scenario('working_bounds',horizon=8)

R1 = S.Resource('R1')
R2 = S.Resource('R2')

T1_s, T1_e = S.Task('T1_s'), S.Task('T1_e')
T1_s += R1
T1_e += R1
S += T1_s + 4 <= T1_e, T1_s >= 0

T2_s, T2_e = S.Task('T2_s'), S.Task('T2_e')
T2_s += R2
T2_e += R2
S += T2_s + 4 <= T2_e#, T2_s >= 2


T = S.Tasks(group='T',n_tasks=6,completion_time_cost=1)
T += R1 | R2
S += T1_s << T#, T << T1_e
S += T2_s << T#, T << T2_e


'''
T = dict()
for i in range(6):
	T[i] = S.Task('T%i'%i,completion_time_cost=-1)
	T[i] += R1 | R2
	S += T[i] << T1_e, T1_s << T[i]
	S += T2_s << T[i], T[i] << T2_e
'''

if solvers.mip.solve(S,msg=1,kind='CBC'):
	plotters.matplotlib.plot(S)
else:
	print('no solution found')
