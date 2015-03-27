#! /usr/bin/env python
from pyschedule import *
import sys

# get input size
n = 5
if len(sys.argv) > 1 :
	n = int(sys.argv[1])

S = Scenario('n queens type scheduling')
R = { i : S.Resource(i) for i in range(n) } #resources
T = { (i,j) : S.Task((i,j)) for i in range(n) for j in range(n) } #tasks

# precedence constrains
S += [ T[(i,j-1)] < T[(i,j)] for i in range(n) for j in range(1,n) ]

# resource assignment modulo n
for i in range(n) :
	R[i] += [ T[((i+j) % n,j)] for j in range(n) ]

solvers.pulp().solve(S,kind='CPLEX',msg=1,lp_filename=None)
plotters.gantt_matplotlib().plot(S,color_prec_groups=True)
