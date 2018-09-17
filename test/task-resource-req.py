# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path.append('../src')

horizon=10

# working day with eight hours
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

solvers.mip.solve(S, msg=0)
print(S.solution())

assert(T0.start_value == 0)
assert(T1.start_value == 1)
#plotters.matplotlib.plot(S, fig_size=(10, 5), vertical_text=True)
