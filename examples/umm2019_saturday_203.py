import sys
sys.path.append('../src')

from pyschedule import Scenario, solvers, plotters, alt

event_duration_in_minutes = 240  #9 * 60
minutes_per_unit = 10

event_duration_in_units = event_duration_in_minutes // minutes_per_unit
scenario = Scenario('umm_saturday', horizon=event_duration_in_units)

Laeufe = scenario.Resource('Läufe')
Weit1 = scenario.Resource('Weit1')
Weit2 = scenario.Resource('Weit2')
Kugel = scenario.Resource('Kugel', size=2)

Gr30 = scenario.Resource('Gr30')

U12M_Gr30_to_Gr34_60m = scenario.Task('U12M_Gr30_60m', length=3, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr30_Pause_1 = scenario.Task('U12M_Gr30_Pause_1', length=1, delay_cost=3, state=-1, plot_color='white')
U12M_Gr30_Weit = scenario.Task('U12M_Gr30_Weit', length=3, delay_cost=2.1, state=1, plot_color='yellow')
U12M_Gr30_Pause_2 = scenario.Task('U12M_Gr30_Pause_2', length=1, delay_cost=2, state=-1, plot_color='white')
U12M_Gr30_Kugel = scenario.Task('U12M_Gr30_Kugel', length=2, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr30_Pause_3 = scenario.Task('U12M_Gr30_Pause_3', length=1, delay_cost=1, state=-1, plot_color='white')
U12M_Gr30_to_Gr34_600m = scenario.Task('U12M_Gr30_to_Gr34_600m', length=3, delay_cost=1, state=1, plot_color='yellow')

#Weit_Pause = scenario.Task('Weit_Pause_1', num=5, is_group=True, length=1, state=-1, plot_color='white')
#Weit_Pause += Weit
Weit_Pause_1 = scenario.Task('Weit_Pause_1', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit_Pause_2 = scenario.Task('Weit_Pause_2', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit_Pause_3 = scenario.Task('Weit_Pause_3', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit_Pause_4 = scenario.Task('Weit_Pause_4', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit_Pause_5 = scenario.Task('Weit_Pause_5', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit_Pause_6 = scenario.Task('Weit_Pause_6', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit_Pause_1 += Weit1
Weit_Pause_2 += Weit1
Weit_Pause_3 += Weit1
Weit_Pause_4 += Weit2
Weit_Pause_5 += Weit2
Weit_Pause_6 += Weit2

#Kugel_Pause = scenario.Task('Kugel_Pause_1', num=5, is_group=True, length=1, state=-1, plot_color='white')
#Kugel_Pause += Kugel
Kugel_Pause_1 = scenario.Task('Kugel_Pause_1', length=1, state=-1, plot_color='white')
Kugel_Pause_2 = scenario.Task('Kugel_Pause_2', length=1, state=-1, plot_color='white')
Kugel_Pause_3 = scenario.Task('Kugel_Pause_3', length=1, state=-1, plot_color='white')
Kugel_Pause_4 = scenario.Task('Kugel_Pause_4', length=1, state=-1, plot_color='white')
Kugel_Pause_5 = scenario.Task('Kugel_Pause_5', length=1, state=-1, plot_color='white')
Kugel_Pause_1 += Kugel
Kugel_Pause_2 += Kugel
Kugel_Pause_3 += Kugel
Kugel_Pause_4 += Kugel
Kugel_Pause_5 += Kugel

U12M_Gr30_to_Gr34_60m += Gr30, Laeufe
U12M_Gr30_Pause_1 += Gr30
U12M_Gr30_Weit += Gr30, Weit1 | Weit2
U12M_Gr30_Pause_2 += Gr30
U12M_Gr30_Kugel += Gr30, Kugel
U12M_Gr30_Pause_3 += Gr30
U12M_Gr30_to_Gr34_600m += Gr30, Laeufe

scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr30_Weit
scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr30_Kugel
scenario += U12M_Gr30_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr30_Kugel < U12M_Gr30_to_Gr34_600m

Gr31 = scenario.Resource('Gr31')

U12M_Gr31_Pause_1 = scenario.Task('U12M_Gr31_Pause_1', length=1, delay_cost=3, state=-1, plot_color='white')
U12M_Gr31_Weit = scenario.Task('U12M_Gr31_Weit', length=3, delay_cost=2.1, state=1, plot_color='yellow')
U12M_Gr31_Pause_2 = scenario.Task('U12M_Gr31_Pause_2', length=1, delay_cost=2, state=-1, plot_color='white')
U12M_Gr31_Kugel = scenario.Task('U12M_Gr31_Kugel', length=2, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr31_Pause_3 = scenario.Task('U12M_Gr31_Pause_3', length=1, delay_cost=1, state=-1, plot_color='white')

U12M_Gr30_to_Gr34_60m += Gr31, Laeufe
U12M_Gr31_Pause_1 += Gr31
U12M_Gr31_Weit += Gr31, Weit1 | Weit2
U12M_Gr31_Pause_2 += Gr31
U12M_Gr31_Kugel += Gr31, Kugel
U12M_Gr31_Pause_3 += Gr31
U12M_Gr30_to_Gr34_600m += Gr31, Laeufe

scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr31_Weit
scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr31_Kugel
scenario += U12M_Gr31_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr31_Kugel < U12M_Gr30_to_Gr34_600m

Gr32 = scenario.Resource('Gr32')

U12M_Gr32_Pause_1 = scenario.Task('U12M_Gr32_Pause_1', length=1, delay_cost=3, state=-1, plot_color='white')
U12M_Gr32_Weit = scenario.Task('U12M_Gr32_Weit', length=3, delay_cost=2.1, state=1, plot_color='yellow')
U12M_Gr32_Pause_2 = scenario.Task('U12M_Gr32_Pause_2', length=1, delay_cost=2, state=-1, plot_color='white')
U12M_Gr32_Kugel = scenario.Task('U12M_Gr32_Kugel', length=2, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr32_Pause_3 = scenario.Task('U12M_Gr32_Pause_3', length=1, delay_cost=1, state=-1, plot_color='white')

U12M_Gr30_to_Gr34_60m += Gr32, Laeufe
U12M_Gr32_Pause_1 += Gr32
U12M_Gr32_Weit += Gr32, Weit1 | Weit2
U12M_Gr32_Pause_2 += Gr32
U12M_Gr32_Kugel += Gr32, Kugel
U12M_Gr32_Pause_3 += Gr32
U12M_Gr30_to_Gr34_600m += Gr32, Laeufe

scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr32_Weit
scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr32_Kugel
scenario += U12M_Gr32_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr32_Kugel < U12M_Gr30_to_Gr34_600m

Gr33 = scenario.Resource('Gr33')

U12M_Gr33_Pause_1 = scenario.Task('U12M_Gr33_Pause_1', length=1, delay_cost=3, state=-1, plot_color='white')
U12M_Gr33_Weit = scenario.Task('U12M_Gr33_Weit', length=3, delay_cost=2.1, state=1, plot_color='yellow')
U12M_Gr33_Pause_2 = scenario.Task('U12M_Gr33_Pause_2', length=1, delay_cost=2, state=-1, plot_color='white')
U12M_Gr33_Kugel = scenario.Task('U12M_Gr33_Kugel', length=2, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr33_Pause_3 = scenario.Task('U12M_Gr33_Pause_3', length=1, delay_cost=1, state=-1, plot_color='white')

U12M_Gr30_to_Gr34_60m += Gr33, Laeufe
U12M_Gr33_Pause_1 += Gr33
U12M_Gr33_Weit += Gr33, Weit1 | Weit2
U12M_Gr33_Pause_2 += Gr33
U12M_Gr33_Kugel += Gr33, Kugel
U12M_Gr33_Pause_3 += Gr33
U12M_Gr30_to_Gr34_600m += Gr33, Laeufe

scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr33_Weit
scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr33_Kugel
scenario += U12M_Gr33_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr33_Kugel < U12M_Gr30_to_Gr34_600m

Gr34 = scenario.Resource('Gr34')

U12M_Gr34_Pause_1 = scenario.Task('U12M_Gr34_Pause_1', length=1, delay_cost=3, state=-1, plot_color='white')
U12M_Gr34_Weit = scenario.Task('U12M_Gr34_Weit', length=3, delay_cost=2.1, state=1, plot_color='yellow')
U12M_Gr34_Pause_2 = scenario.Task('U12M_Gr34_Pause_2', length=1, delay_cost=2, state=-1, plot_color='white')
U12M_Gr34_Kugel = scenario.Task('U12M_Gr34_Kugel', length=2, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr34_Pause_3 = scenario.Task('U12M_Gr34_Pause_3', length=1, delay_cost=1, state=-1, plot_color='white')

U12M_Gr30_to_Gr34_60m += Gr34, Laeufe
U12M_Gr34_Pause_1 += Gr34
U12M_Gr34_Weit += Gr34, Weit1 | Weit2
U12M_Gr34_Pause_2 += Gr34
U12M_Gr34_Kugel += Gr34, Kugel
U12M_Gr34_Pause_3 += Gr34
U12M_Gr30_to_Gr34_600m += Gr34, Laeufe

scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr34_Weit
scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr34_Kugel
scenario += U12M_Gr34_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr34_Kugel < U12M_Gr30_to_Gr34_600m


for i in range(event_duration_in_units):
    scenario += Gr30['state'][:i] <= 1
    scenario += Gr30['state'][:i] >= 0
    scenario += Gr31['state'][:i] <= 1
    scenario += Gr31['state'][:i] >= 0
    scenario += Gr32['state'][:i] <= 1
    scenario += Gr32['state'][:i] >= 0
    scenario += Gr33['state'][:i] <= 1
    scenario += Gr33['state'][:i] >= 0
    scenario += Gr34['state'][:i] <= 1
    scenario += Gr34['state'][:i] >= 0
    scenario += Weit1['state'][:i] <= 1
    scenario += Weit1['state'][:i] >= 0
    scenario += Weit2['state'][:i] <= 1
    scenario += Weit2['state'][:i] >= 0
    scenario += Kugel['state'][:i] <= 1
    scenario += Kugel['state'][:i] >= 0


print("scenario: {}".format(scenario))


#import pdb; pdb.set_trace()
if solvers.mip.solve(scenario, time_limit=600, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True, img_filename='umm_saturday.png', fig_size=(45, 5))
else:
    print('no solution found')
    assert(1==0)
