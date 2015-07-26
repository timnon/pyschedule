#! /usr/bin/python
import pyschedule
import sys

# get input size
n = 3

S = pyschedule.Scenario('n queens type scheduling')
R = { i : S.Resource(i) for i in range(n) } #resources
T = { (i,j) : S.Task((i,j)) for i in range(n) for j in range(n) } #tasks

# precedence constrains
S += [ T[i,j-1] < T[i,j] for i in range(n) for j in range(1,n) ]

# resource assignment modulo n
for i in range(n) :
	S += R[i] % [ T[(i+j) % n,j] for j in range(n) ]

S.use_makespan_objective()
pyschedule.solvers.pulp.solve(S,msg=1)
pyschedule.plotters.matplotlib.plot(S,color_prec_groups=False)
