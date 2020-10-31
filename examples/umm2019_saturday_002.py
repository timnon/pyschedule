import sys
sys.path.append('../src')
from pyschedule import Scenario, solvers, plotters, alt


scenario = Scenario('umm_saturday', horizon=144)

disziplinen = {
        "U12W_4K": {
                "Disziplinen": {
                        "60m": 'Läufe',
                        "Weit": 'Weit',
                        "Kugel": 'Kugel',
                        "600m": 'Läufe',
                },
                "Color": "orange",
        },
        "U16W_5K": {
                "Disziplinen": {
                        "80m": 'Läufe',
                        "Weit": 'Weit',
                        "Kugel": 'Kugel',
                        "Hoch": 'Hoch',
                        "1000m": 'Läufe',
                },
                "Color": "pink",
        },
        "WOM_7K": {
                "Disziplinen": {
                        "100mHü": 'Läufe',
                        "Hoch": 'Hoch',
                        "Kugel": 'Kugel',
                        "200m": 'Läufe',
                },
                "Color": "lightgreen",
        },
        "U12M_4K": {
                "Disziplinen": {
                        "60m": 'Läufe',
                        "Weit": 'Weit',
                        "Kugel": 'Kugel',
                        "600m": 'Läufe',
                },
                "Color": "yellow",
        },
        "U16M_6K": {
                "Disziplinen": {
                        "100mHü": 'Läufe',
                        "Weit": 'Weit',
                        "Kugel": 'Kugel',
                        "Hoch": 'Hoch',
                        "Diskus": 'Diskus',
                        "1000m": 'Läufe',
                },
                "Color": "lightblue",
        },
        "MAN_10K": {
                "Disziplinen": {
                        "100m": 'Läufe',
                        "Weit": 'Weit',
                        "Kugel": 'Kugel',
                        "Hoch": 'Hoch',
                        "400m": 'Läufe',
                },
                "Color": "red",
        },
}

teilnehmer = {
        "U12W_4K": {
                "Gr14": 13,
                "Gr15": 12,
                "Gr16": 12,
                "Gr17": 12,
                "Gr18": 12,
                "Gr19": 12,
                "Gr20": 12,
        },
        "U16W_5K": {
                "Gr3": 10,
                "Gr4": 10,
                "Gr5": 11,
                "Gr6": 11,
        },
        "WOM_7K": {
                "Gr1": 11,
                "Gr2": 14,
        },
        "U12M_4K": {
                "Gr30": 12,
                "Gr31": 13,
                "Gr32": 11,
                "Gr33": 12,
                "Gr34": 11,
        },
        "U16M_6K": {
                "Gr24": 11,
                "Gr25": 10,
        },
        "MAN_10K": {
                "Gr23": 9,
        },
}

anlagen = {
        "Läufe": 1,
        "Weit": 2,
        "Hoch": 2,
        "Kugel": 2,
        "Diskus": 1,
}


# setup resources
resource = {}
print("anlagen:")
for name, num_instances in anlagen.items():
        print("  anlage={!r}, num={!r}".format(name, num_instances))
        resource[name] = scenario.Resource(name, size=num_instances)
print("groups:")
for _, groups in teilnehmer.items():
        for name, _ in groups.items():
                print("  name={!r}".format(name))
                resource[name] = scenario.Resource(name)


# setup tasks
task = {}
print("tasks:")
for wettkampf_name, wettkampf in disziplinen.items():
        disziplinen = wettkampf["Disziplinen"]
        color = wettkampf["Color"]
        first_group_name = next(iter(teilnehmer[wettkampf_name]))
        for group_name, num_group_members in teilnehmer[wettkampf_name].items():
                tasks = []
                for disziplin_name, resource_name in disziplinen.items():
                    task_name = "{}_{}_{}".format(wettkampf_name, group_name, disziplin_name)
                    if disziplin_name in ("600m", "1000m") and group_name == first_group_name:
                            last_task_name = task_name
                    if disziplin_name in ("600m", "1000m") and group_name != first_group_name:
                            pass
                    else:
                            print("  name={!r} resource={}".format(task_name, resource_name))
                            t = scenario.Task(task_name, length=2, delay_cost=1, plot_color=color)
                            t += resource[resource_name], resource[group_name]
                            tasks.append(t)
                            task[task_name] = t
                task_iter = iter(tasks)
                current_task = next(task_iter)
                for next_task in task_iter:
                        scenario += current_task + 2 < next_task
                        current_task = next_task
                if group_name != first_group_name:
                        scenario += current_task + 2 < task[last_task_name]

print("scenario={}".format(scenario))

if solvers.mip.solve(scenario, time_limit=600, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True, img_filename='tmp.png', fig_size=(100,10))
else:
    print('no solution found')
    assert(1==0)
