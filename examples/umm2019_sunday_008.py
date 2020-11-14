import sys
sys.path.append('../src')

import argparse
from collections import defaultdict
import functools
import operator
from pyschedule import Scenario, solvers, plotters, alt


parser = argparse.ArgumentParser(description='calculate event timetable')
parser.add_argument('--print-scenario-and-exit', action="store_true",
                    help='print scenario and exit')
default_time_limit = '10m'
help_text = 'time limit, e.g. 30s, 10m, 1h (default: {})'.format(default_time_limit)
parser.add_argument('--time-limit', default=default_time_limit, help=help_text)
valid_wettkampf_days = ['saturday', 'sunday']
parser.add_argument('day', type=str.lower, choices=valid_wettkampf_days, help='wettkampf day')
args = parser.parse_args()
if args.time_limit.endswith('s'):
    args.time_limit = float(args.time_limit[:-1])
elif args.time_limit.endswith('m'):
    args.time_limit = float(args.time_limit[:-1]) * 60
elif args.time_limit.endswith('h'):
    args.time_limit = float(args.time_limit[:-1]) * 3600
else:
    args.time_limit = float(args.time_limit)
#print('args: {}'.format(args))

event_duration_in_minutes = 10 * 60  # 09:00..18:00 + 1h (margin)
minutes_per_unit = 10

event_duration_in_units = event_duration_in_minutes // minutes_per_unit
scenario = Scenario('umm_saturday', horizon=event_duration_in_units)

print('creating anlagen...')
anlagen = {}


class AnlagenDescriptor(object):
    def __init__(self, name, size=1):
        self._name = name
        self._size = size

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size


def create_anlage(descriptor):
    for i in range(descriptor.size):
        anlagen_name = descriptor.name
        if descriptor.size > 1:
            anlagen_name += "{}".format(i + 1)
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


anlagen_descriptors = [
    AnlagenDescriptor("Läufe"),
    AnlagenDescriptor("Weit", 2),
    AnlagenDescriptor("Kugel", 2),
    AnlagenDescriptor("Hoch", 2),
    AnlagenDescriptor("Diskus"),
    AnlagenDescriptor("Speer"),
    AnlagenDescriptor("Stab"),
]
for anlagen_descriptor in anlagen_descriptors:
    create_anlage(anlagen_descriptor)


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


wettkampf_start_times = {
    "U14M_5K_Gr26_to_Gr29_60m": 0,
    "MAN_6K_Gr35_to_Gr37_100m": 4,
    "WOM_5K_Gr21_to_Gr22_100m": 10,
    "MAN_10K_Gr23_to_Gr23_110mHü": 14,
    "U14W_5K_Gr7_to_Gr13_60m": 18,
    "WOM_7K_Gr1_to_Gr2_Weit": 23,
}

wettkampf_duration_budget = {
    "U14M_5K": 26,
    "MAN_6K": 41,
    "WOM_5K": 28,
    "MAN_10K": 39,
    "U14W_5K": 31,
    "WOM_7K": 18,
}

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

print('creating disziplinen...')
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
                print('  {}'.format(disziplinen_name))
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
        objective_terms.append(last_disziplin * (1 + 1) - first_disziplin)

print('creating anlagen pauses...')
for anlage, num_disziplinen in used_anlagen.items():
    for candidate in anlagen.values():
        if candidate.name.startswith(anlage):
            for i in range(num_disziplinen):
                task_name = "{}_Pause_{}".format(candidate, i + 1)
                task = scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
                task += candidate
                hide_tasks.append(task)

print('forcing wettkampf start times...')
for disziplinen_name, start_times in wettkampf_start_times.items():
    try:
        scenario += disziplinen[disziplinen_name] >= start_times
    except KeyError:
        pass

print('ensuring pauses for groups and anlagen...')
for i in range(event_duration_in_units):
    for gruppe in sequence_not_strict_gruppen:
        scenario += gruppe['state'][:i] <= 1
        scenario += gruppe['state'][:i] >= 0
    for _, anlage in anlagen.items():
        scenario += anlage['state'][:i] <= 1
        scenario += anlage['state'][:i] >= 0

print('assembling objective...')
scenario.clear_objective()
for objective_term in set(objective_terms):
    scenario += objective_term
print("objective: {}".format(scenario.objective()))

if args.print_scenario_and_exit:
    print("scenario: {}".format(scenario))
    sys.exit()

if solvers.mip.solve(scenario, time_limit=args.time_limit, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True, img_filename='umm2019_{}.png'.format(args.day), fig_size=(100, 5), hide_tasks=hide_tasks)
else:
    print('no solution found')
    assert(1==0)
