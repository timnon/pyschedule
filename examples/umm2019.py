import argparse
import datetime
import logging
import os
import sys

import athletics_event


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
os.mkdir(output_folder_name)
link_name = "latest"
if os.path.exists(link_name):
    os.remove(link_name)
os.symlink(output_folder_name, link_name)
os.chdir(output_folder_name)


log_level = logging.INFO
if args.verbose:
    log_level=logging.DEBUG
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('{}.log'.format(event_name))
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
root_logger.addHandler(ch)
root_logger.addHandler(fh)
matplotlib_logger = logging.getLogger("matplotlib")
matplotlib_logger.setLevel(logging.INFO)


logging.debug('output folder: {!r}'.format(output_folder_name))


event_duration_in_minutes = 12 * 60  # 09:00..18:00 + 3h (margin)
minutes_per_unit = 10

event_duration_in_units = event_duration_in_minutes // minutes_per_unit


anlagen_descriptors = {
    'saturday': [
        ("Läufe",),
        ("Weit", 2),
        ("Kugel", 2),
        ("Hoch", 2),
        ("Diskus",),
    ],
    'sunday': [
        ("Läufe",),
        ("Weit", 2),
        ("Kugel", 2),
        ("Hoch", 2),
        ("Diskus",),
        ("Speer",),
        ("Stab",),
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
            dict(name="1000m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="lightblue")),
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
            dict(name="Pause_3", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='red')),
            dict(name="Speer", together=False, resource="Speer", kwargs=dict(length=3, state=1, plot_color="red")),
            dict(name="Pause_4", together=False, resource=None, kwargs=dict(length=3, state=-1, plot_color='red')),
            dict(name="1500m", together=True, resource="Läufe", kwargs=dict(length=1, state=1, plot_color="red")),
        ],
        "U14W_5K": [
            dict(name="60m", together=True, resource="Läufe", kwargs=dict(length=3, state=1, plot_color="pink")),  # FIXME: actual length should be 5
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
            dict(name="800m", together=True, resource="Läufe", kwargs=dict(length=2, state=1, plot_color="lightgreen")),
        ],
    }
}


last_wettkampf_of_the_day = "MAN_10K"


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


event = athletics_event.AthleticsEventScheduler(
    name=event_name, duration_in_units=event_duration_in_units,
    wettkampf_budget_data=wettkampf_budget_data[args.day])
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
    logging.info("scenario: {}".format(scenario_as_string))
    sys.exit()
logging.info("scenario: {}".format(scenario_as_string))
event.solve(args.time_limit)
