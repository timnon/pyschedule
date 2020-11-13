import sys
sys.path.append('../src')

from collections import defaultdict
import functools
import operator
from pyschedule import Scenario, solvers, plotters, alt

event_duration_in_minutes = 18 * 60  # 09:00..18:00
minutes_per_unit = 10

event_duration_in_units = event_duration_in_minutes // minutes_per_unit
scenario = Scenario('umm_saturday', horizon=event_duration_in_units)

anlagen = {}


def create_anlage(name, size=1):
    resources = []
    for i in range(size):
        anlagen_name = name
        if size > 1:
            anlagen_name = "{}{}".format(name, i + 1)
        anlage = scenario.Resource(anlagen_name)
        anlagen[anlagen_name] = anlage


def get_all_anlagen(pattern):
    resources = []
    for anlagen_name, anlage in anlagen.items():
        if anlagen_name.startswith(pattern):
            resources.append(anlage)
    return resources


def any_anlage(pattern):
    return functools.reduce(lambda a, b: operator.or_(a, b), get_all_anlagen(item["resource"]))


create_anlage("Läufe")
create_anlage("Weit", 2)
create_anlage("Kugel", 2)
create_anlage("Hoch", 2)
create_anlage("Diskus")
create_anlage("Speer", 2)
create_anlage("Stab")


used_anlagen = defaultdict(int)

disziplinen_data = {
    "U14M_5K": [
        dict(name="60m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="orange")),
        dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='orange')),
        dict(name="Weit", together=False, resource="Weit", kwargs=dict(length=3, state=1, plot_color="orange")),
        dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='orange')),
        dict(name="Kugel", together=False, resource="Kugel", kwargs=dict(length=2, state=1, plot_color="orange")),
        dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='orange')),
        dict(name="Hoch", together=False, resource="Hoch", kwargs=dict(length=3, state=1, plot_color="orange")),
        dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='orange')),
        dict(name="600m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="orange")),
    ],
    "MAN_6K": [
        dict(name="100m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="lightblue")),
        dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
        dict(name="Weit", together=False, resource="Weit", kwargs=dict(length=3, state=1, plot_color="lightblue")),
        dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
        dict(name="Kugel", together=False, resource="Kugel", kwargs=dict(length=2, state=1, plot_color="lightblue")),
        dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
        dict(name="Hoch", together=False, resource="Hoch", kwargs=dict(length=3, state=1, plot_color="lightblue")),
        dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
        dict(name="Speer", together=False, resource="Speer", kwargs=dict(length=3, state=1, plot_color="lightblue")),
        dict(name="Pause_5", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
        dict(name="600m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="lightblue")),
    ],
    "WOM_5K": [
        dict(name="100m", together=True, resource="Läufe", kwargs=dict(length=2, state=1, plot_color="olive")),
        dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='olive')),
        dict(name="Weit", together=False, resource="Weit", kwargs=dict(length=3, state=1, plot_color="olive")),
        dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='olive')),
        dict(name="Kugel", together=False, resource="Kugel", kwargs=dict(length=2, state=1, plot_color="olive")),
        dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='olive')),
        dict(name="Hoch", together=False, resource="Hoch", kwargs=dict(length=3, state=1, plot_color="olive")),
        dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='olive')),
        dict(name="1000m", together=True, resource="Läufe", kwargs=dict(length=2, state=1, plot_color="olive")),
    ],
    "MAN_10K": [
        dict(name="110mHü", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="red")),
        dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='red')),
        dict(name="Diskus", together=False, resource="Diskus", kwargs=dict(length=2, state=1, plot_color="red")),
        dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=4, state=-1, plot_color='red')),
        dict(name="Stab", together=False, resource="Stab", kwargs=dict(length=11, state=1, plot_color="red")),
        dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=6, state=-1, plot_color='red')),
        dict(name="Speer", together=False, resource="Speer", kwargs=dict(length=3, state=1, plot_color="red")),
        dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='red')),
        dict(name="1500m", together=False, resource="Läufe", kwargs=dict(length=1, state=1, plot_color="red")),
    ],
    "U14W_5K": [
        dict(name="60m", together=True, resource="Läufe", kwargs=dict(length=5, state=1, plot_color="pink")),
        dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='pink')),
        dict(name="Weit", together=False, resource="Weit", kwargs=dict(length=3, state=1, plot_color="pink")),
        dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='pink')),
        dict(name="Kugel", together=False, resource="Kugel", kwargs=dict(length=2, state=1, plot_color="pink")),
        dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='pink')),
        dict(name="Hoch", together=False, resource="Hoch", kwargs=dict(length=3, state=1, plot_color="pink")),
        dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='pink')),
        dict(name="600m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="pink")),
    ],
    "WOM_7K": [
        dict(name="Weit", together=True, resource="Weit", kwargs=dict(length=3, state=1, plot_color="lightgreen")),
        dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='lightgreen')),
        dict(name="Speer", together=False, resource="Speer", kwargs=dict(length=3, state=1, plot_color="lightgreen")),
        dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='lightgreen')),
        dict(name="200m", together=False, resource="Läufe", kwargs=dict(length=2, state=1, plot_color="lightgreen")),
    ],
}

disziplinen_sequence_strict_data = ["MAN_10K", "WOM_7K"]


def is_wettkampf_disziplinen_sequence_strict(wettkampf_name):
    return wettkampf_name in disziplinen_sequence_strict_data


teilnehmer_data = {
    "U14M_5K": {
        "Gr26": 12,
        "Gr27": 12,
        "Gr28": 12,
        "Gr29": 12,
        },
    "MAN_6K": {
        "Gr35": 12,
        "Gr36": 13,
        "Gr37": 17,
    },        
    "WOM_5K": {
        "Gr21": 8,
        "Gr22": 14,
    },
    "MAN_10K": {
        "Gr23": 9,
    },
    "U14W_5K": {
        "Gr7": 13,
        "Gr8": 13,
        "Gr9": 13,
        "Gr10": 13,
        "Gr11": 13,
        "Gr12": 13,
        "Gr13": 13,
    },
    "WOM_7K": {
        "Gr1": 11,
        "Gr2": 14,
    },
}

objective_terms = []
gruppen = {}
sequence_not_strict_gruppen = []
disziplinen = {}
hide_tasks = []
for wettkampf_name in disziplinen_data:
    gruppen_names = list(teilnehmer_data[wettkampf_name].keys())
    for gruppen_name in gruppen_names:
        gruppe = scenario.Resource(gruppen_name)
        gruppen[gruppen_name] = gruppe
        gruppen_disziplinen = []
        for item in disziplinen_data[wettkampf_name]:
            disziplinen_name = "{}_{}_{}".format(wettkampf_name, gruppen_name, item["name"])
            if item["together"]:
                disziplinen_name = "{}_{}_to_{}_{}".format(wettkampf_name, gruppen_names[0], gruppen_names[-1], item["name"])
            if disziplinen_name not in disziplinen.keys():
                disziplin = scenario.Task(disziplinen_name, **item['kwargs'])
                disziplinen[disziplinen_name] = disziplin
            else:
                disziplin = disziplinen[disziplinen_name]
            gruppen_disziplinen.append(disziplin)
    
            if item["resource"]:
                used_anlagen[item["resource"]] += 1
                if not item["together"] or gruppen_name == gruppen_names[0]:
                    disziplin += any_anlage(item["resource"])

            disziplin += gruppe

            if "Pause" in disziplinen_name:
                hide_tasks.append(disziplin)

        first_disziplin = gruppen_disziplinen[0]
        last_disziplin = gruppen_disziplinen[-1]
        if is_wettkampf_disziplinen_sequence_strict(wettkampf_name):
            # one after another: 1st, 2nd, 3rd,...
            current_disziplin = gruppen_disziplinen[0]
            for next_disziplin in gruppen_disziplinen[1:]:
                scenario += current_disziplin < next_disziplin
                current_disziplin = next_disziplin
        else:
            # 1st and last together - rest free
            for disziplin in gruppen_disziplinen[1:-1]:
                if "Pause" in disziplin.name:
                    continue
                scenario += first_disziplin < disziplin
    
            for disziplin in gruppen_disziplinen[1:-1]:
                if "Pause" in disziplin.name:
                    continue
                scenario += disziplin < last_disziplin
            sequence_not_strict_gruppen.append(gruppe)
        objective_terms.append(last_disziplin * (1 + 2) - first_disziplin)

for anlage, num_disziplinen in used_anlagen.items():
    for candidate in anlagen.values():
        if candidate.name.startswith(anlage):
            for i in range(num_disziplinen):
                task_name = "{}_Pause_{}".format(candidate, i + 1)
                task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
                task += candidate
                hide_tasks.append(task)


scenario += disziplinen["U14M_5K_Gr26_to_Gr29_60m"] >= 0
scenario += disziplinen["MAN_6K_Gr35_to_Gr37_100m"] >= 4
scenario += disziplinen["WOM_5K_Gr21_to_Gr22_100m"] >= 10
scenario += disziplinen["MAN_10K_Gr23_to_Gr23_110mHü"] >= 14
scenario += disziplinen["U14W_5K_Gr7_to_Gr13_60m"] >= 18
scenario += disziplinen["WOM_7K_Gr1_to_Gr2_Weit"] >= 23


for i in range(event_duration_in_units):
    for gruppe in sequence_not_strict_gruppen:
        scenario += gruppe['state'][:i] <= 1
        scenario += gruppe['state'][:i] >= 0
    for _, anlage in anlagen.items():
        scenario += anlage['state'][:i] <= 1
        scenario += anlage['state'][:i] >= 0

scenario.clear_objective()
for objective_term in set(objective_terms):
    scenario += objective_term

#print("scenario: {}".format(scenario))

if solvers.mip.solve(scenario, time_limit=3*3600, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True, img_filename='umm_sunday.png', fig_size=(60, 5), hide_tasks=hide_tasks)
else:
    print('no solution found')
    assert(1==0)
