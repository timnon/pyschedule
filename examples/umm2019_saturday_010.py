# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path.append('../src')
import getopt
opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
from pyschedule import Scenario, solvers, plotters, alt

event_duration_in_minutes = 9 * 60
minutes_per_unit = 1
event_duration_in_units = event_duration_in_minutes // minutes_per_unit
scenario = Scenario('umm_saturday', horizon=event_duration_in_units)

Laeufe = scenario.Resource('Läufe')
Weit = scenario.Resource('Weit', size=2)
Kugel = scenario.Resource('Kugel', size=2)

Gr30 = scenario.Resource('Gr30')
Gr31 = scenario.Resource('Gr31')
Gr32 = scenario.Resource('Gr32')
Gr33 = scenario.Resource('Gr33')
Gr34 = scenario.Resource('Gr34')

U12M_Gr30_60m = scenario.Task('U12M_Gr30_60m', length=6, delay_cost=2, state=1, plot_color='yellow')
U12M_Gr30_Pause_1 = scenario.Task('U12M_Gr30_Pause_1', length=30, delay_cost=1, state=-1, plot_color='white')
U12M_Gr30_Weit = scenario.Task('U12M_Gr30_Weit', length=30, delay_cost=2, state=1, plot_color='yellow')
U12M_Gr30_Pause_2 = scenario.Task('U12M_Gr30_Pause_2', length=10, delay_cost=1, state=-1, plot_color='white')
U12M_Gr30_Kugel = scenario.Task('U12M_Gr30_Kugel', length=20, delay_cost=2, state=1, plot_color='yellow')
U12M_Gr30_Pause_3 = scenario.Task('U12M_Gr30_Pause_3', length=20, delay_cost=1, state=-1, plot_color='white')
U12M_Gr30_to_Gr34_600m = scenario.Task('U12M_Gr30_to_Gr34_600m', length=24, delay_cost=2, state=1, plot_color='yellow')
U12M_Gr31_60m = scenario.Task('U12M_Gr31_60m', length=6, delay_cost=2, plot_color='yellow')
U12M_Gr31_Pause_1 = scenario.Task('U12M_Gr31_Pause_1', length=30, delay_cost=1, state=-1, plot_color='white')
U12M_Gr31_Weit = scenario.Task('U12M_Gr31_Weit', length=30, delay_cost=2, plot_color='yellow')
U12M_Gr31_Pause_2 = scenario.Task('U12M_Gr31_Pause_2', length=10, delay_cost=1, state=-1, plot_color='white')
U12M_Gr31_Kugel = scenario.Task('U12M_Gr31_Kugel', length=20, delay_cost=2, plot_color='yellow')
U12M_Gr31_Pause_3 = scenario.Task('U12M_Gr31_Pause_3', length=20, delay_cost=1, state=-1, plot_color='white')
U12M_Gr32_60m = scenario.Task('U12M_Gr32_60m', length=6, delay_cost=2, plot_color='yellow')
U12M_Gr32_Pause_1 = scenario.Task('U12M_Gr32_Pause_1', length=30, delay_cost=1, state=-1, plot_color='white')
U12M_Gr32_Weit = scenario.Task('U12M_Gr32_Weit', length=30, delay_cost=2, plot_color='yellow')
U12M_Gr32_Pause_2 = scenario.Task('U12M_Gr32_Pause_2', length=10, delay_cost=1, state=-1, plot_color='white')
U12M_Gr32_Kugel = scenario.Task('U12M_Gr32_Kugel', length=20, delay_cost=2, plot_color='yellow')
U12M_Gr32_Pause_3 = scenario.Task('U12M_Gr32_Pause_3', length=20, delay_cost=1, state=-1, plot_color='white')
U12M_Gr33_60m = scenario.Task('U12M_Gr33_60m', length=6, delay_cost=2, plot_color='yellow')
U12M_Gr33_Pause_1 = scenario.Task('U12M_Gr33_Pause_1', length=30, delay_cost=1, state=-1, plot_color='white')
U12M_Gr33_Weit = scenario.Task('U12M_Gr33_Weit', length=30, delay_cost=2, plot_color='yellow')
U12M_Gr33_Pause_2 = scenario.Task('U12M_Gr33_Pause_2', length=10, delay_cost=1, state=-1, plot_color='white')
U12M_Gr33_Kugel = scenario.Task('U12M_Gr33_Kugel', length=20, delay_cost=2, plot_color='yellow')
U12M_Gr33_Pause_3 = scenario.Task('U12M_Gr33_Pause_3', length=20, delay_cost=1, state=-1, plot_color='white')
U12M_Gr34_60m = scenario.Task('U12M_Gr34_60m', length=6, delay_cost=2, plot_color='yellow')
U12M_Gr34_Pause_1 = scenario.Task('U12M_Gr34_Pause_1', length=30, delay_cost=1, state=-1, plot_color='white')
U12M_Gr34_Weit = scenario.Task('U12M_Gr34_Weit', length=30, delay_cost=2, plot_color='yellow')
U12M_Gr34_Pause_2 = scenario.Task('U12M_Gr34_Pause_2', length=10, delay_cost=1, state=-1, plot_color='white')
U12M_Gr34_Kugel = scenario.Task('U12M_Gr34_Kugel', length=20, delay_cost=2, plot_color='yellow')
U12M_Gr34_Pause_3 = scenario.Task('U12M_Gr34_Pause_3', length=20, delay_cost=1, state=-1, plot_color='white')

U12M_Gr30_60m += Laeufe, Gr30
U12M_Gr31_60m += Laeufe, Gr31
U12M_Gr32_60m += Laeufe, Gr32
U12M_Gr33_60m += Laeufe, Gr33
U12M_Gr34_60m += Laeufe, Gr34

U12M_Gr30_Pause_1 += Gr30
U12M_Gr31_Pause_1 += Gr31
U12M_Gr32_Pause_1 += Gr32
U12M_Gr33_Pause_1 += Gr33
U12M_Gr34_Pause_1 += Gr34

U12M_Gr30_Weit += Weit, Gr30
U12M_Gr31_Weit += Weit, Gr31
U12M_Gr32_Weit += Weit, Gr32
U12M_Gr33_Weit += Weit, Gr33
U12M_Gr34_Weit += Weit, Gr34

U12M_Gr30_Pause_2 += Gr30
U12M_Gr31_Pause_2 += Gr31
U12M_Gr32_Pause_2 += Gr32
U12M_Gr33_Pause_2 += Gr33
U12M_Gr34_Pause_2 += Gr34

U12M_Gr30_Kugel += Kugel, Gr30
U12M_Gr31_Kugel += Kugel, Gr31
U12M_Gr32_Kugel += Kugel, Gr32
U12M_Gr33_Kugel += Kugel, Gr33
U12M_Gr34_Kugel += Kugel, Gr34

U12M_Gr30_Pause_3 += Gr30
U12M_Gr31_Pause_3 += Gr31
U12M_Gr32_Pause_3 += Gr32
U12M_Gr33_Pause_3 += Gr33
U12M_Gr34_Pause_3 += Gr34

U12M_Gr30_to_Gr34_600m +=  Laeufe, Gr30

scenario += U12M_Gr30_60m < U12M_Gr31_60m
scenario += U12M_Gr31_60m < U12M_Gr32_60m
scenario += U12M_Gr32_60m < U12M_Gr33_60m
scenario += U12M_Gr33_60m < U12M_Gr34_60m

scenario += U12M_Gr30_60m < U12M_Gr30_Weit
scenario += U12M_Gr30_60m < U12M_Gr30_Kugel
scenario += U12M_Gr30_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr30_Kugel < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr31_60m < U12M_Gr31_Weit
scenario += U12M_Gr31_60m < U12M_Gr31_Kugel
scenario += U12M_Gr31_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr31_Kugel < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr32_60m < U12M_Gr32_Weit
scenario += U12M_Gr32_60m < U12M_Gr32_Kugel
scenario += U12M_Gr32_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr32_Kugel < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr33_60m < U12M_Gr33_Weit
scenario += U12M_Gr33_60m < U12M_Gr33_Kugel
scenario += U12M_Gr33_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr33_Kugel < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr34_60m < U12M_Gr34_Weit
scenario += U12M_Gr34_60m < U12M_Gr34_Kugel
scenario += U12M_Gr34_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr34_Kugel < U12M_Gr30_to_Gr34_600m


for t in range(event_duration_in_units):
    scenario += Gr30['state'][:t] <= 1
    scenario += Gr30['state'][:t] >= 0
    scenario += Gr31['state'][:t] <= 1
    scenario += Gr31['state'][:t] >= 0


print("scenario: {}".format(scenario))

if solvers.mip.solve(scenario, time_limit=600, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True)
else:
    print('no solution found')
    assert(1==0)
