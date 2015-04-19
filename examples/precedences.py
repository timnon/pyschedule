#! /usr/bin/env python
from pyschedule import *

S = Scenario('precedences')

I1 = S.Task('I1')
I2 = S.Task('I2')
I3 = S.Task('I3')
I4 = S.Task('I4')
MakeSpan = S.Task('MakeSpan')

S += MakeSpan
S += MakeSpan > { I1, I2, I3, I4 }

S += I1 < I2, I2 < I3, I3 < I4

solvers.pulp.solve(S,msg=1)
plotters.matplotlib.plot(S)
