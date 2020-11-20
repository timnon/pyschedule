import sys
sys.path.append('../src')

import argparse
from collections import defaultdict
import datetime
import functools
import operator
import os
from pyschedule import Scenario, solvers, plotters, alt


parser = argparse.ArgumentParser(description='calculate event timetable')
parser.add_argument('--print-scenario-and-exit', action="store_true",
                    help='print scenario and exit')
default_time_limit = '10m'
help_text = 'time limit, e.g. 30s, 10m, 1h (default: {})'.format(default_time_limit)
parser.add_argument('-v', '--verbose', action="store_true", help="be verbose")
parser.add_argument('--time-limit', default=default_time_limit, help=help_text)
parser.add_argument('--dont-set-start-time', action="store_true", help="don't set start time")
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


start_time = datetime.datetime.now()
event_name = "{}_{}".format(os.path.splitext(__file__)[0], args.day)
output_folder_name = "{}_{}".format(start_time.isoformat(timespec="seconds"), event_name)
if args.verbose:
    print('creating output folder {!r}...'.format(output_folder_name))
os.mkdir(output_folder_name)
os.chdir(output_folder_name)


event_duration_in_minutes = 12 * 60  # 09:00..18:00 + 3h (margin)
minutes_per_unit = 10

event_duration_in_units = event_duration_in_minutes // minutes_per_unit


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


anlagen_descriptors = {
    'saturday': [
        AnlagenDescriptor("Läufe"),
        AnlagenDescriptor("Weit", 2),
        AnlagenDescriptor("Kugel", 2),
        AnlagenDescriptor("Hoch", 2),
        AnlagenDescriptor("Diskus"),
    ],
    'sunday': [
        AnlagenDescriptor("Läufe"),
        AnlagenDescriptor("Weit", 2),
        AnlagenDescriptor("Kugel", 2),
        AnlagenDescriptor("Hoch", 2),
        AnlagenDescriptor("Diskus"),
        AnlagenDescriptor("Speer"),
        AnlagenDescriptor("Stab"),
    ],
}


disziplinen_data = {
    'saturday': {
        "U12W_4K": [
            dict(name="60m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="orange")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit", sequence_free=True, kwargs=dict(length=3, state=1, plot_color="orange")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=True, kwargs=dict(length=2, state=1, plot_color="orange")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="orange")),
        ],
        "U16W_5K": [
            dict(name="80m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="pink")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="pink")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="pink")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Hoch", together=False, resource="Hoch", sequence_free=False, kwargs=dict(length=4, state=1, plot_color="pink")),
            dict(name="Pause_4", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="pink")),
        ],
        "WOM_7K": [
            dict(name="100mHü", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="lightgreen")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="Hoch", together=False, resource="Hoch", sequence_free=False, kwargs=dict(length=4, state=1, plot_color="lightgreen")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="lightgreen")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="200m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="lightgreen")),
        ],
        "U12M_4K": [
            dict(name="60m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="yellow")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit", sequence_free=True, kwargs=dict(length=3, state=1, plot_color="yellow")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=True, kwargs=dict(length=2, state=1, plot_color="yellow")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="yellow")),
        ],
        "U16M_6K": [
            dict(name="100mHü", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="lightblue")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="lightblue")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="lightblue")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="Hoch", together=False, resource="Hoch", sequence_free=False, kwargs=dict(length=4, state=1, plot_color="lightblue")),
            dict(name="Pause_4", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="Diskus", together=True, resource="Diskus", sequence_free=False, kwargs=dict(length=5, state=1, plot_color="lightblue")),
            dict(name="Pause_5", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="1000m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="lightblue")),
        ],
        "MAN_10K": [
            dict(name="100m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=1, state=1, plot_color="red")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=5, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit1&Weit2", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="red")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=3, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel1&Kugel2", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="red")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=4, state=-1, plot_color='white')),
            dict(name="Hoch", together=False, resource="Hoch1&Hoch2", sequence_free=False, kwargs=dict(length=4, state=1, plot_color="red")),
            dict(name="Pause_4", together=False, resource=None, sequence_free=False, kwargs=dict(length=4, state=-1, plot_color='white')),
            dict(name="400m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=2, state=1, plot_color="red")),
        ],
    },
    "sunday": {
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
            dict(name="Kugel", together=False, resource="Kugel1&Kugel2", kwargs=dict(length=2, state=1, plot_color="lightblue")),
            dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
            dict(name="Hoch", together=False, resource="Hoch", kwargs=dict(length=3, state=1, plot_color="lightblue")),
            dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
            dict(name="Speer", together=False, resource="Speer", kwargs=dict(length=3, state=1, plot_color="lightblue")),
            dict(name="Pause_5", together=False, resource=None, kwargs=dict(length=1, state=-1, plot_color='lightblue')),
            dict(name="600m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="lightblue")),
        ],
        "WOM_5K": [
            dict(name="100m", together=True, resource="Läufe", kwargs=dict(length=2, state=1, plot_color="olive")),
            dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='olive')),
            dict(name="Weit", together=False, resource="Weit", kwargs=dict(length=3, state=1, plot_color="olive")),
            dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='olive')),
            dict(name="Kugel", together=False, resource="Kugel", kwargs=dict(length=2, state=1, plot_color="olive")),
            dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='olive')),
            dict(name="Hoch", together=False, resource="Hoch", kwargs=dict(length=3, state=1, plot_color="olive")),
            dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='olive')),
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
            dict(name="1500m", together=True, resource="Läufe", kwargs=dict(length=1, state=1, plot_color="red")),
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
            dict(name="Weit", together=True, resource="Weit1&Weit2", kwargs=dict(length=3, state=1, plot_color="lightgreen")),
            dict(name="Pause_1", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='lightgreen')),
            dict(name="Speer", together=True, resource="Speer", kwargs=dict(length=6, state=1, plot_color="lightgreen")),
            dict(name="Pause_2", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='lightgreen')),
            dict(name="200m", together=False, resource="Läufe", kwargs=dict(length=2, state=1, plot_color="lightgreen")),
        ],
    }
}

last_wettkampf_of_the_day = "MAN_10K"

disziplinen_sequence_strict_data = ["MAN_10K", "WOM_7K", "U16M_6K", "U16W_5K"]


def is_wettkampf_disziplinen_sequence_strict(wettkampf_name):
    return wettkampf_name in disziplinen_sequence_strict_data


wettkampf_start_times = {
    "saturday": {
        "U12M_4K_Gr30_to_Gr34_60m": 0,
        "U16M_6K_Gr24_to_Gr25_100mHü": 6,
        "WOM_7K_Gr1_to_Gr2_100mHü": 9,
        "U16W_5K_Gr3_to_Gr6_80m": 13,
        "MAN_10K_Gr23_to_Gr23_100m": 20,
        "U12W_4K_Gr14_to_Gr20_60m": 22,
    },
    "sunday": {
        "U14M_5K_Gr26_to_Gr29_60m": 0,
        "MAN_6K_Gr35_to_Gr37_100m": 4,
        "WOM_5K_Gr21_to_Gr22_100m": 10,
        "MAN_10K_Gr23_to_Gr23_110mHü": 14,
        "U14W_5K_Gr7_to_Gr13_60m": 18,
        "WOM_7K_Gr1_to_Gr2_Weit": 23,
    },
}

wettkampf_budget_data = {
    "saturday": {
        "U12W_4K": (22, 49),
        "U16W_5K": (13, 42),
        "WOM_7K": (9, 35),
        "U12M_4K": (0, 27),
        "U16M_6K": (6, 45),
        "MAN_10K": (20, 53),
    },
    "sunday": {
        "U14W_5K": (18, 49),
        "WOM_7K": (23, 41),
        "WOM_5K": (10, 38),
        "U14M_5K": (0, 26),
        "MAN_10K": (14,53),
        "MAN_6K": (4, 45),
    },
}


def get_objective_weight_factors(wettkampf_name):
    sum_of_event_end_times = 0
    for _, end_time in wettkampf_budget_data[args.day].values():
        sum_of_event_end_times += end_time
    event_end_time_factor = 500. / sum_of_event_end_times
    event_start_time, event_end_time = wettkampf_budget_data[args.day][wettkampf_name]
    event_duration = event_end_time - event_start_time
    event_duration_factor = 100. / event_duration
    return (round(event_end_time_factor + event_duration_factor), round(event_duration_factor))


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
    "U14W_5K": {
        "Gr7": 13,
        "Gr8": 13,
        "Gr9": 13,
        "Gr10": 13,
        "Gr11": 13,
        "Gr12": 13,
        "Gr13": 13,
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
    "WOM_5K": {
        "Gr21": 8,
        "Gr22": 14,
    },
    "U12M_4K": {
        "Gr30": 12,
        "Gr31": 13,
        "Gr32": 11,
        "Gr33": 12,
        "Gr34": 11,
    },
    "U14M_5K": {
        "Gr26": 12,
        "Gr27": 12,
        "Gr28": 12,
        "Gr29": 12,
    },
    "U16M_6K": {
        "Gr24": 11,
        "Gr25": 10,
    },
    "MAN_10K": {
        "Gr23": 9,
    },
    "MAN_6K": {
        "Gr35": 12,
        "Gr36": 13,
        "Gr37": 17,
    },
}


class AthleticsEventScheduler(object):
    def __init__(self, name, duration_in_units, verbose):
        self._name = name
        self._duration_in_units = duration_in_units
        self._verbose = verbose
        self._anlagen = {}
        self._objective_terms = {}
        self._used_anlagen = defaultdict(int)
        self._disziplinen = {}
        self._hide_tasks = []
        self._sequence_not_strict_gruppen = []
        self.create_scenario()

    def create_scenario(self):
        self._scenario = Scenario(self._name, horizon=self._duration_in_units)

    @property
    def scenario(self):
        return self._scenario

    def create_anlagen(self, descriptors):
        if self._verbose:
            print('creating anlagen...')
        for descriptor in descriptors:
            self._create_anlage(descriptor)

    def _create_anlage(self, descriptor):
        for i in range(descriptor.size):
            anlagen_name = descriptor.name
            if descriptor.size > 1:
                anlagen_name += "{}".format(i + 1)
            print("  {}".format(anlagen_name))
            anlage = self._scenario.Resource(anlagen_name)
            self._anlagen[anlagen_name] = anlage

    def any_anlage(self, pattern):
        return functools.reduce(lambda a, b: operator.or_(a, b), self._get_all_anlagen(pattern))

    def _get_all_anlagen(self, pattern):
        resources = []
        for anlagen_name, anlage in self._anlagen.items():
            if anlagen_name.startswith(pattern):
                resources.append(anlage)
        return resources

    def create_disziplinen(self, disziplinen_data, teilnehmer_data):
        gruppen = {}
        if self._verbose:
            print('creating disziplinen...')
        for wettkampf_name in disziplinen_data:
            if self._verbose:
                print("  wettkampf: {}".format(wettkampf_name))
            gruppen_names = list(teilnehmer_data[wettkampf_name].keys())
            for gruppen_name in gruppen_names:
                if self._verbose:
                    print("    gruppe: {}".format(gruppen_name))
                gruppe = self._scenario.Resource(gruppen_name)
                gruppen[gruppen_name] = gruppe
                gruppen_disziplinen = []
                for item in disziplinen_data[wettkampf_name]:
                    disziplinen_name = "{}_{}_{}".format(wettkampf_name, gruppen_name, item["name"])
                    if item["together"]:
                        disziplinen_name = "{}_{}_to_{}_{}".format(wettkampf_name, gruppen_names[0], gruppen_names[-1], item["name"])
                    if disziplinen_name not in self._disziplinen.keys():
                        disziplin = self._scenario.Task(disziplinen_name, **item['kwargs'])
                        self._disziplinen[disziplinen_name] = disziplin
                    else:
                        disziplin = self._disziplinen[disziplinen_name]
                    gruppen_disziplinen.append(disziplin)

                    if item["resource"]:
                        resource_base_name = item["resource"]
                        resource_names = item["resource"].split("&")
                        if resource_names[0][-1].isdigit():
                            resource_base_name = resource_names[0][:-1]
                        self._used_anlagen[resource_base_name] += 1
                        if not item["together"] or gruppen_name == gruppen_names[0]:
                            for resource_name in resource_names:
                                disziplin += event.any_anlage(resource_name)

                    disziplin += gruppe

                    if "Pause" in disziplinen_name:
                        self._hide_tasks.append(disziplin)

                first_disziplin = gruppen_disziplinen[0]
                last_disziplin = gruppen_disziplinen[-1]
                if is_wettkampf_disziplinen_sequence_strict(wettkampf_name):
                    # one after another: 1st, 2nd, 3rd,...
                    current_disziplin = gruppen_disziplinen[0]
                    for next_disziplin in gruppen_disziplinen[1:]:
                        self._scenario += current_disziplin < next_disziplin
                        current_disziplin = next_disziplin
                else:
                    # 1st and last set - rest free
                    for disziplin in gruppen_disziplinen[1:-1]:
                        if "Pause" in disziplin.name:
                            continue
                        self._scenario += first_disziplin < disziplin

                    for disziplin in gruppen_disziplinen[1:-1]:
                        if "Pause" in disziplin.name:
                            continue
                        self._scenario += disziplin < last_disziplin
                    self._sequence_not_strict_gruppen.append(gruppe)
            objective_weight_factors = get_objective_weight_factors(wettkampf_name)
            self._objective_terms[wettkampf_name] = {
                "formula": last_disziplin * objective_weight_factors[0] - first_disziplin * objective_weight_factors[1],
                "last_disziplin": last_disziplin,
            }

    def create_anlagen_pausen(self):
        if self._verbose:
            print('creating anlagen pausen...')
        for anlage, num_disziplinen in self._used_anlagen.items():
            for candidate in self._anlagen.values():
                if candidate.name.startswith(anlage):
                    for i in range(num_disziplinen):
                        task_name = "{}_Pause_{}".format(candidate, i + 1)
                        task = self._scenario.Task(task_name, length=1, schedule_cost=-1, state=-1, plot_color='white')
                        task += candidate
                        self._hide_tasks.append(task)

    def set_wettkampf_start_times(self, wettkampf_start_times):
        if args.verbose:
            print('setting wettkampf start times...')
        for disziplinen_name, start_times in wettkampf_start_times.items():
            try:
                self._scenario += self._disziplinen[disziplinen_name] >= start_times
            except KeyError:
                pass

    def ensure_pausen_for_gruppen_and_anlagen(self):
        if self._verbose:
            print('ensuring pausen for groups and anlagen...')
        for i in range(self._duration_in_units):
            for gruppe in self._sequence_not_strict_gruppen:
                self._scenario += gruppe['state'][:i] <= 1
                self._scenario += gruppe['state'][:i] >= 0
            for _, anlage in self._anlagen.items():
                self._scenario += anlage['state'][:i] <= 1
                self._scenario += anlage['state'][:i] >= 0

    def ensure_last_wettkampf_of_the_day(self, last_wettkampf_of_the_day):
        if self._verbose:
            print('ensuring last wettkampf of the day...')
        last_disziplin_of_the_day = self._objective_terms[last_wettkampf_of_the_day]["last_disziplin"]
        for wettkampf_name, objective_term in self._objective_terms.items():
            if wettkampf_name != last_wettkampf_of_the_day:
                self._scenario += objective_term["last_disziplin"] < last_disziplin_of_the_day
        
    def set_objective(self):
        if self._verbose:
            print('setting objective...')
        self._scenario.clear_objective()
        for objective_term in self._objective_terms.values():
            self._scenario += objective_term["formula"]

    def solve(self, time_limit):
        if self._verbose:
            print('solving problem...')
        if solvers.mip.solve(self._scenario, time_limit=time_limit, msg=1):
            solution_as_string = str(self._scenario.solution())
            solution_filename = '{}_solution.txt'.format(self._name)
            with open(solution_filename, 'w') as f:
                f.write(solution_as_string)
            print(solution_as_string)
            plotters.matplotlib.plot(self._scenario, show_task_labels=True, img_filename='{}.png'.format(self._name),
                                     fig_size=(100, 5), hide_tasks=self._hide_tasks)
        else:
            print('no solution found')
            assert(1==0)
        

event = AthleticsEventScheduler(name=event_name, duration_in_units=event_duration_in_units, verbose=args.verbose)
event.create_anlagen(anlagen_descriptors[args.day])
event.create_disziplinen(disziplinen_data[args.day], teilnehmer_data)
event.create_anlagen_pausen()
if not args.dont_set_start_time:
    event.set_wettkampf_start_times(wettkampf_start_times[args.day])
event.ensure_pausen_for_gruppen_and_anlagen()
event.ensure_last_wettkampf_of_the_day(last_wettkampf_of_the_day)
event.set_objective()
scenario_as_string = str(event.scenario)
scenario_filename = '{}_scenario.txt'.format(event_name)
with open(scenario_filename, 'w') as f:
    f.write(scenario_as_string)
if args.print_scenario_and_exit:
    print("scenario: {}".format(scenario_as_string))
    sys.exit()
if args.verbose:
    print("scenario: {}".format(scenario_as_string))
event.solve(args.time_limit)
