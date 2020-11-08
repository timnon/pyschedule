import sys
sys.path.append('../src')

from pyschedule import Scenario, solvers, plotters, alt

event_duration_in_minutes = 240
minutes_per_unit = 10

event_duration_in_units = event_duration_in_minutes // minutes_per_unit
scenario = Scenario('umm_saturday', horizon=event_duration_in_units)

anlagen_names = ["Läufe", "Weit1", "Weit2", "Kugel1", "Kugel2"]
anlagen = {}
for anlagen_name in anlagen_names:
    anlage = scenario.Resource(anlagen_name)
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
hide_tasks = []
for gruppen_name in gruppen_names:
    gruppe = scenario.Resource(gruppen_name)
    gruppen[gruppen_name] = gruppe
    gruppen_disziplinen = []
    for item in disziplinen_data:
        disziplinen_name = "{}_{}_{}".format(wettkampf_name, gruppen_name, item["name"])
        if item["together"]:
            disziplinen_name = "{}_{}_to_{}_{}".format(wettkampf_name, gruppen_names[0], gruppen_names[-1], item["name"])
        if disziplinen_name not in disziplinen.keys():
            disziplin = scenario.Task(disziplinen_name, **item['kwargs'])
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

        if "Pause" in disziplinen_name:
            hide_tasks.append(disziplin)

    print("gruppen_disziplinen: {}".format(gruppen_disziplinen))
    first_disziplin = gruppen_disziplinen[0]
    for disziplin in gruppen_disziplinen[1:-1]:
        if "Pause" in disziplin.name:
            continue
        scenario += first_disziplin < disziplin

    last_disziplin = gruppen_disziplinen[-1]
    for disziplin in gruppen_disziplinen[1:-1]:
        if "Pause" in disziplin.name:
            continue
        scenario += disziplin < last_disziplin

task_name = "Läufe_Pause"
task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
task += anlagen["Läufe"]
hide_tasks.append(task)

for gruppen_name in gruppen_names:
    task_name = "Weit1_Pause_{}".format(gruppen_name)
    task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Weit1"]
    hide_tasks.append(task)
    task_name = "Weit2_Pause_{}".format(gruppen_name)
    task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Weit2"]
    hide_tasks.append(task)

for gruppen_name in gruppen_names:
    task_name = "Kugel1_Pause_{}".format(gruppen_name)
    task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Kugel1"]
    hide_tasks.append(task)

for gruppen_name in gruppen_names:
    task_name = "Kugel2_Pause_{}".format(gruppen_name)
    task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
    task += anlagen["Kugel2"]
    hide_tasks.append(task)


for i in range(event_duration_in_units):
    for _, gruppe in gruppen.items():
        scenario += gruppe['state'][:i] <= 1
        scenario += gruppe['state'][:i] >= 0
    for _, anlage in anlagen.items():
        scenario += anlage['state'][:i] <= 1
        scenario += anlage['state'][:i] >= 0

print("scenario: {}".format(scenario))

if solvers.mip.solve(scenario, time_limit=600, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True, img_filename='umm_saturday.png', fig_size=(45, 5), hide_tasks=hide_tasks)
else:
    print('no solution found')
    assert(1==0)

