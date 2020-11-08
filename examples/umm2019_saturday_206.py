import sys
sys.path.append('../src')

from pyschedule import Scenario, solvers, plotters, alt

event_duration_in_minutes = 240
minutes_per_unit = 10

event_duration_in_units = event_duration_in_minutes // minutes_per_unit
scenario = Scenario('umm_saturday', horizon=event_duration_in_units)

Laeufe = scenario.Resource('Läufe')
Weit1 = scenario.Resource('Weit1')
Weit2 = scenario.Resource('Weit2')
Kugel1 = scenario.Resource('Kugel1')
Kugel2 = scenario.Resource('Kugel2')

Gr30 = scenario.Resource('Gr30')

U12M_Gr30_to_Gr34_60m = scenario.Task('U12M_Gr30_to_Gr34_60m', length=3, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr30_Pause_1 = scenario.Task('U12M_Gr30_Pause_1', length=1, delay_cost=3, state=-1, plot_color='white')
U12M_Gr30_Weit = scenario.Task('U12M_Gr30_Weit', length=3, delay_cost=2.1, state=1, plot_color='yellow')
U12M_Gr30_Pause_2 = scenario.Task('U12M_Gr30_Pause_2', length=1, delay_cost=2, state=-1, plot_color='white')
U12M_Gr30_Kugel = scenario.Task('U12M_Gr30_Kugel', length=2, delay_cost=1, state=1, plot_color='yellow')
U12M_Gr30_Pause_3 = scenario.Task('U12M_Gr30_Pause_3', length=1, delay_cost=1, state=-1, plot_color='white')
U12M_Gr30_to_Gr34_600m = scenario.Task('U12M_Gr30_to_Gr34_600m', length=3, delay_cost=1, state=1, plot_color='yellow')

U12M_Gr30_to_Gr34_60m += Gr30, Laeufe
U12M_Gr30_Pause_1 += Gr30
U12M_Gr30_Weit += Gr30, Weit1 | Weit2
U12M_Gr30_Pause_2 += Gr30
U12M_Gr30_Kugel += Gr30, Kugel1 | Kugel2
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
U12M_Gr31_Kugel += Gr31, Kugel1 | Kugel2
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
U12M_Gr32_Kugel += Gr32, Kugel1 | Kugel2
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
U12M_Gr33_Kugel += Gr33, Kugel1 | Kugel2
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
U12M_Gr34_Kugel += Gr34, Kugel1 | Kugel2
U12M_Gr34_Pause_3 += Gr34
U12M_Gr30_to_Gr34_600m += Gr34, Laeufe

scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr34_Weit
scenario += U12M_Gr30_to_Gr34_60m < U12M_Gr34_Kugel
scenario += U12M_Gr34_Weit < U12M_Gr30_to_Gr34_600m
scenario += U12M_Gr34_Kugel < U12M_Gr30_to_Gr34_600m

Weit1_Pause_Gr30 = scenario.Task('Weit1_Pause_Gr30', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit2_Pause_Gr30 = scenario.Task('Weit2_Pause_Gr30', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit1_Pause_Gr31 = scenario.Task('Weit1_Pause_Gr31', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit2_Pause_Gr31 = scenario.Task('Weit2_Pause_Gr31', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit1_Pause_Gr32 = scenario.Task('Weit1_Pause_Gr32', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit2_Pause_Gr32 = scenario.Task('Weit2_Pause_Gr32', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit1_Pause_Gr33 = scenario.Task('Weit1_Pause_Gr33', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit2_Pause_Gr33 = scenario.Task('Weit2_Pause_Gr33', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit1_Pause_Gr34 = scenario.Task('Weit1_Pause_Gr34', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit2_Pause_Gr34 = scenario.Task('Weit2_Pause_Gr34', length=1, schedule_cost=-1, state=-1, plot_color='white')
Weit1_Pause_Gr30 += Weit1
Weit1_Pause_Gr31 += Weit1
Weit1_Pause_Gr32 += Weit1
Weit1_Pause_Gr33 += Weit1
Weit1_Pause_Gr34 += Weit1
Weit1_Pause_Gr30 += Weit2
Weit1_Pause_Gr31 += Weit2
Weit1_Pause_Gr32 += Weit2
Weit1_Pause_Gr33 += Weit2
Weit1_Pause_Gr34 += Weit2

Kugel1_Pause_Gr30 = scenario.Task('Kugel1_Pause_Gr30', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel1_Pause_Gr31 = scenario.Task('Kugel1_Pause_Gr31', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel1_Pause_Gr32 = scenario.Task('Kugel1_Pause_Gr32', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel1_Pause_Gr33 = scenario.Task('Kugel1_Pause_Gr33', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel1_Pause_Gr34 = scenario.Task('Kugel1_Pause_Gr34', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel2_Pause_Gr30 = scenario.Task('Kugel2_Pause_Gr30', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel2_Pause_Gr31 = scenario.Task('Kugel2_Pause_Gr31', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel2_Pause_Gr32 = scenario.Task('Kugel2_Pause_Gr32', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel2_Pause_Gr33 = scenario.Task('Kugel2_Pause_Gr33', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel2_Pause_Gr34 = scenario.Task('Kugel2_Pause_Gr34', length=1, schedule_cost=-1, state=-1, plot_color='white')
Kugel1_Pause_Gr30 += Kugel1
Kugel1_Pause_Gr31 += Kugel1
Kugel1_Pause_Gr32 += Kugel1
Kugel1_Pause_Gr33 += Kugel1
Kugel1_Pause_Gr34 += Kugel1
Kugel2_Pause_Gr30 += Kugel2
Kugel2_Pause_Gr31 += Kugel2
Kugel2_Pause_Gr32 += Kugel2
Kugel2_Pause_Gr33 += Kugel2
Kugel2_Pause_Gr34 += Kugel2

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
    scenario += Kugel1['state'][:i] <= 1
    scenario += Kugel1['state'][:i] >= 0
    scenario += Kugel2['state'][:i] <= 1
    scenario += Kugel2['state'][:i] >= 0

#print("scenario: {}".format(scenario))

#if solvers.mip.solve(scenario, time_limit=600, msg=1):
#    print(scenario.solution())
#    plotters.matplotlib.plot(scenario, show_task_labels=True, img_filename='umm_saturday.png', fig_size=(45, 5))
#else:
#    print('no solution found')
#    assert(1==0)


scenario2 = Scenario('umm_saturday', horizon=event_duration_in_units)

anlagen_names = ["Läufe", "Weit1", "Weit2", "Kugel1", "Kugel2"]
anlagen = {}
for anlagen_name in anlagen_names:
    anlage = scenario2.Resource(anlagen_name)
    anlagen[anlagen_name] = anlage


wettkampf_name = "U12M"
color = "yellow"
gruppen_names = ["Gr30", "Gr31", "Gr32", "Gr33", "Gr34"]
gruppen = {}
disziplinen_data = [
    dict(name="60m", together=True, resource="Läufe", kwargs=dict(length=3, delay_cost=1, state=1, plot_color=color)),
    dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=1, delay_cost=3, state=-1, plot_color='white')),
    dict(name="Weit", together=False, resource="Weit", kwargs=dict(length=3, delay_cost=2.1, state=1, plot_color=color)),
    dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=1, delay_cost=2, state=-1, plot_color='white')),
    dict(name="Kugel", together=False, resource="Kugel", kwargs=dict(length=2, delay_cost=1, state=1, plot_color=color)),
    dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=1, delay_cost=1, state=-1, plot_color='white')),
    dict(name="600m", together=True, resource="Läufe", kwargs=dict(length=3, delay_cost=1, state=1, plot_color=color)),
]
disziplinen = {}
for gruppen_name in gruppen_names:
    gruppe = scenario2.Resource(gruppen_name)
    gruppen[gruppen_name] = gruppe
    gruppen_disziplinen = []
    for item in disziplinen_data:
        disziplinen_name = "{}_{}_{}".format(wettkampf_name, gruppen_name, item["name"])
        if item["together"]:
            disziplinen_name = "{}_{}_to_{}_{}".format(wettkampf_name, gruppen_names[0], gruppen_names[-1], item["name"])
        if disziplinen_name not in disziplinen.keys():
            disziplin = scenario2.Task(disziplinen_name, **item['kwargs'])
            disziplinen[disziplinen_name] = disziplin
        else:
            disziplin = disziplinen[disziplinen_name]
        gruppen_disziplinen.append(disziplin)

        disziplin += gruppe
        if item["resource"] == "Läufe":
            disziplin += anlagen["Läufe"]
        if item["resource"] == "Weit":
            disziplin += anlagen["Weit1"] | anlagen["Weit2"]
        if item["resource"] == "Kugel":
            disziplin += anlagen["Kugel1"] | anlagen["Kugel2"]

    print("gruppen_disziplinen: {}".format(gruppen_disziplinen))
    first_disziplin = gruppen_disziplinen[0]
    for disziplin in gruppen_disziplinen[1:-1]:
        if disziplin.name.find('Pause') >= 0:
            continue
        scenario2 += first_disziplin < disziplin

    last_disziplin = gruppen_disziplinen[-1]
    for disziplin in gruppen_disziplinen[1:-1]:
        if disziplin.name.find('Pause') >= 0:
            continue
        scenario2 += disziplin < last_disziplin

for gruppen_name in gruppen_names:
    task_name = "Weit1_Pause_{}".format(gruppen_name)
    task = scenario2.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Weit1"]
    task_name = "Weit2_Pause_{}".format(gruppen_name)
    task = scenario2.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Weit2"]

for gruppen_name in gruppen_names:
    task_name = "Kugel1_Pause_{}".format(gruppen_name)
    task = scenario2.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Kugel1"]

for gruppen_name in gruppen_names:
    task_name = "Kugel2_Pause_{}".format(gruppen_name)
    task = scenario2.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Kugel2"]


for i in range(event_duration_in_units):
    scenario2 += gruppen["Gr30"]['state'][:i] <= 1
    scenario2 += gruppen["Gr30"]['state'][:i] >= 0
    scenario2 += gruppen["Gr31"]['state'][:i] <= 1
    scenario2 += gruppen["Gr31"]['state'][:i] >= 0
    scenario2 += gruppen["Gr32"]['state'][:i] <= 1
    scenario2 += gruppen["Gr32"]['state'][:i] >= 0
    scenario2 += gruppen["Gr33"]['state'][:i] <= 1
    scenario2 += gruppen["Gr33"]['state'][:i] >= 0
    scenario2 += gruppen["Gr34"]['state'][:i] <= 1
    scenario2 += gruppen["Gr34"]['state'][:i] >= 0
    scenario2 += anlagen["Weit1"]['state'][:i] <= 1
    scenario2 += anlagen["Weit1"]['state'][:i] >= 0
    scenario2 += anlagen["Weit2"]['state'][:i] <= 1
    scenario2 += anlagen["Weit2"]['state'][:i] >= 0
    scenario2 += anlagen["Kugel1"]['state'][:i] <= 1
    scenario2 += anlagen["Kugel1"]['state'][:i] >= 0
    scenario2 += anlagen["Kugel2"]['state'][:i] <= 1
    scenario2 += anlagen["Kugel2"]['state'][:i] >= 0

print("scenario2: {}".format(scenario2))

if solvers.mip.solve(scenario2, time_limit=600, msg=1):
    print(scenario2.solution())
    plotters.matplotlib.plot(scenario2, show_task_labels=True, img_filename='umm_saturday.png', fig_size=(45, 5))
else:
    print('no solution found')
    assert(1==0)

assert str(scenario.resources()) == str(scenario2.resources())
assert str(scenario.tasks()) == str(scenario2.tasks())
#print("constraints: {}\n".format(scenario.constraints()))
print("constraints2: {}\n".format(scenario2.constraints()))
assert str(scenario.constraints()) == str(scenario2.constraints())

