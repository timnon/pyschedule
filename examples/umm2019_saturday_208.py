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


create_anlage("Läufe")
create_anlage("Weit", 2)
create_anlage("Kugel", 2)
create_anlage("Hoch")
create_anlage("Diskus")

used_anlagen = defaultdict(int)

disziplinen_data = {
    "U12W_4K": [
        dict(name="60m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, delay_cost=1, state=1, plot_color="orange")),
        dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=3, state=-1, plot_color='white')),
        dict(name="Weit", together=False, resource="Weit", sequence_free=True, kwargs=dict(length=3, delay_cost=2.1, state=1, plot_color="orange")),
        dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=2, state=-1, plot_color='white')),
        dict(name="Kugel", together=False, resource="Kugel", sequence_free=True, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="orange")),
        dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=1, state=-1, plot_color='white')),
        dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, delay_cost=1, state=1, plot_color="orange")),
    ],
    "U16W_5K": [
        dict(name="80m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, delay_cost=1, state=1, plot_color="pink")),
        dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=4, state=-1, plot_color='white')),
        dict(name="Weit", together=False, resource="Weit", sequence_free=False, kwargs=dict(length=3, delay_cost=2.1, state=1, plot_color="pink")),
        dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=3, state=-1, plot_color='white')),
        dict(name="Kugel", together=False, resource="Kugel", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="pink")),
        dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=2, state=-1, plot_color='white')),
        dict(name="Hoch", together=False, resource="Hoch", sequence_free=False, kwargs=dict(length=4, delay_cost=2.1, state=1, plot_color="pink")),
        dict(name="Pause_4", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=1, state=-1, plot_color='white')),
        dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, delay_cost=1, state=1, plot_color="pink")),
    ],
    "WOM_7K": [
        dict(name="100mHü", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, delay_cost=1, state=1, plot_color="lightgreen")),
        dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=3, state=-1, plot_color='white')),
        dict(name="Hoch", together=False, resource="Hoch", sequence_free=False, kwargs=dict(length=4, delay_cost=2.1, state=1, plot_color="lightgreen")),
        dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=2, state=-1, plot_color='white')),
        dict(name="Kugel", together=False, resource="Kugel", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="lightgreen")),
        dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=1, state=-1, plot_color='white')),
        dict(name="200m", together=False, resource="Läufe", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="lightgreen")),
    ],
    "U12M_4K": [
        dict(name="60m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, delay_cost=1, state=1, plot_color="yellow")),
        dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=3, state=-1, plot_color='white')),
        dict(name="Weit", together=False, resource="Weit", sequence_free=True, kwargs=dict(length=3, delay_cost=2.1, state=1, plot_color="yellow")),
        dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=2, state=-1, plot_color='white')),
        dict(name="Kugel", together=False, resource="Kugel", sequence_free=True, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="yellow")),
        dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=1, state=-1, plot_color='white')),
        dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, delay_cost=1, state=1, plot_color="yellow")),
    ],
    "U16M_6K": [
        dict(name="100mHü", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="lightblue")),
        dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=5, state=-1, plot_color='white')),
        dict(name="Weit", together=False, resource="Weit", sequence_free=False, kwargs=dict(length=3, delay_cost=2.1, state=1, plot_color="lightblue")),
        dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=4, state=-1, plot_color='white')),
        dict(name="Kugel", together=False, resource="Kugel", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="lightblue")),
        dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=3, state=-1, plot_color='white')),
        dict(name="Hoch", together=False, resource="Hoch", sequence_free=False, kwargs=dict(length=4, delay_cost=2.1, state=1, plot_color="lightblue")),
        dict(name="Pause_4", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=2, state=-1, plot_color='white')),
        dict(name="Diskus", together=False, resource="Diskus", sequence_free=False, kwargs=dict(length=3, delay_cost=2.1, state=1, plot_color="lightblue")),
        dict(name="Pause_5", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, delay_cost=1, state=-1, plot_color='white')),
        dict(name="1000m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="lightblue")),
    ],
    "MAN_10K": [
        dict(name="100m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=1, delay_cost=1, state=1, plot_color="red")),
        dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=5, delay_cost=5, state=-1, plot_color='white')),
        dict(name="Weit", together=False, resource="Weit", sequence_free=False, kwargs=dict(length=3, delay_cost=2.1, state=1, plot_color="red")),
        dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, delay_cost=4, state=-1, plot_color='white')),
        dict(name="Kugel", together=False, resource="Kugel", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="red")),
        dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=4, delay_cost=3, state=-1, plot_color='white')),
        dict(name="Hoch", together=False, resource="Hoch", sequence_free=False, kwargs=dict(length=4, delay_cost=2.1, state=1, plot_color="red")),
        dict(name="Pause_4", together=False, resource=None, sequence_free=False, kwargs=dict(length=2, delay_cost=2, state=-1, plot_color='white')),
        dict(name="400m", together=False, resource="Läufe", sequence_free=False, kwargs=dict(length=2, delay_cost=1, state=1, plot_color="red")),
    ],
}

teilnehmer_data = {
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

objective_pairs = []
gruppen = {}
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
                    disziplin += functools.reduce(lambda a, b: operator.or_(a, b), get_all_anlagen(item["resource"]))

            disziplin += gruppe

            if "Pause" in disziplinen_name:
                hide_tasks.append(disziplin)

        first_disziplin = gruppen_disziplinen[0]
        last_disziplin = gruppen_disziplinen[-1]
        if False:
            for disziplin in gruppen_disziplinen[1:-1]:
                if "Pause" in disziplin.name:
                    continue
                scenario += first_disziplin < disziplin
    
            for disziplin in gruppen_disziplinen[1:-1]:
                if "Pause" in disziplin.name:
                    continue
                scenario += disziplin < last_disziplin
        else:
            current_disziplin = gruppen_disziplinen[0]
            for next_disziplin in gruppen_disziplinen[1:]:
                scenario += current_disziplin < next_disziplin
                current_disziplin = next_disziplin
        objective_pairs.append((last_disziplin, first_disziplin))

for anlage, num_disziplinen in used_anlagen.items():
    for candidate in anlagen.values():
        if candidate.name.startswith(anlage):
            for i in range(num_disziplinen):
                task_name = "{}_Pause_{}".format(candidate, i + 1)
                task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
                task += candidate
                hide_tasks.append(task)


scenario += disziplinen["U12M_4K_Gr30_to_Gr34_60m"] >= 0
scenario += disziplinen["U16M_6K_Gr24_to_Gr25_100mHü"] >= 6
scenario += disziplinen["WOM_7K_Gr1_to_Gr2_100mHü"] >= 9
scenario += disziplinen["U16W_5K_Gr3_to_Gr6_80m"] >= 13
scenario += disziplinen["MAN_10K_Gr23_to_Gr23_100m"] >= 20
scenario += disziplinen["U12W_4K_Gr14_to_Gr20_60m"] >= 22


for i in range(event_duration_in_units):
    #for _, gruppe in gruppen.items():
    #    scenario += gruppe['state'][:i] <= 1
    #    scenario += gruppe['state'][:i] >= 0
    for _, anlage in anlagen.items():
        scenario += anlage['state'][:i] <= 1
        scenario += anlage['state'][:i] >= 0

scenario.clear_objective()
for op1, op2 in objective_pairs:
    scenario += op1 * 2 - op2

#print("scenario: {}".format(scenario))

if solvers.mip.solve(scenario, time_limit=None, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True, img_filename='umm_saturday.png', fig_size=(45, 5), hide_tasks=hide_tasks)
else:
    print('no solution found')
    assert(1==0)
