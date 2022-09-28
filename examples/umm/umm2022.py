import datetime
import logging
import os
import sys

import athletics_event


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

wettkampf_data = {
    'saturday': {
        "U12W_4K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "orange",
        },
        "U16W_5K": {
            "disziplinen": [
                dict(name="80m", together=True, resource="Läufe", length=2),
                dict(name="Pause_1", length=3),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=3),
                dict(name="Hoch", resource="Hoch", length=5),
                dict(name="Pause_4", length=3),
                dict(name="600m", together=True, resource="Läufe", length=2),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "plot_color": "pink",
        },
        "WOM_7K": {
            "disziplinen": [
                dict(name="100mHü", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=3),
                dict(name="Hoch", together=True, resource="Hoch1&Hoch2", use_num_anlagen=2, length=5),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", together=True, resource="Kugel1&Kugel2", use_num_anlagen=2, length=3),
                dict(name="Pause_3", length=3),
                dict(name="200m", together=True, resource="Läufe", length=2),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "plot_color": "lightgreen",
        },
        "U12M_4K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "yellow",
        },
        "U16M_6K": {
            "disziplinen": [
                dict(name="100mHü", together=True, resource="Läufe", length=2),
                dict(name="Pause_1", length=3),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=3),
                dict(name="Hoch", resource="Hoch", length=5),
                dict(name="Pause_4", length=3),
                dict(name="Diskus", together=True, resource="Diskus", length=5),
                dict(name="Pause_5", length=3),
                dict(name="1000m", together=True, resource="Läufe", length=2),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "plot_color": "lightblue",
        },
        "MAN_10K": {
            "disziplinen": [
                dict(name="100m", together=True, resource="Läufe", length=2),
                dict(name="Pause_1", length=5),
                dict(name="Weit", together=True, resource="Weit1&Weit2", use_num_anlagen=2, length=3),  # auf Weit1 und Weit2
                dict(name="Pause_2", length=3),
                dict(name="Kugel", together=True, resource="Kugel1&Kugel2", length=4),  # nur auf Kugel1
                dict(name="Pause_3", length=4),
                dict(name="Hoch", together=True, resource="Hoch1&Hoch2", use_num_anlagen=2, length=7),  # auf Hoch1 und Hoch2
                dict(name="Pause_4", length=4),
                dict(name="400m", together=True, resource="Läufe", length=3),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "is_last_wettkampf_of_the_day": True,
            "plot_color": "red",
        },
    },
    "sunday": {
        "U14M_5K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="Hoch", resource="Hoch", length=3),
                dict(name="Pause_4", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "orange",
        },
        "MAN_6K": {
            "disziplinen": [
                dict(name="100m", together=True, resource="Läufe", length=2),
                dict(name="Pause_1", length=3),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel1&Kugel2", length=2),
                dict(name="Pause_3", length=3),
                dict(name="Hoch", resource="Hoch", length=3),
                dict(name="Pause_4", length=3),
                dict(name="Speer", resource="Speer", length=3),
                dict(name="Pause_5", length=3),
                dict(name="1000m", together=True, resource="Läufe", length=2),
            ],
            "plot_color": "lightblue",
        },
        "WOM_5K": {
            "disziplinen": [
                dict(name="100m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=3),
                dict(name="Weit", resource="Weit", length=4),
                dict(name="Pause_2", length=3),
                dict(name="Kugel", resource="Kugel", length=3),
                dict(name="Pause_3", length=3),
                dict(name="Hoch", resource="Hoch", length=4),
                dict(name="Pause_4", length=3),
                dict(name="1000m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "olive",
        },
        "MAN_10K": {
            "disziplinen": [
                dict(name="110mHü", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=3),
                dict(name="Diskus", together=True, resource="Diskus&Speer", length=4),
                dict(name="Pause_2", length=4),
                dict(name="Stab", together=True, resource="Stab&Speer", length=9),
                dict(name="Pause_3", length=3),
                dict(name="Speer", together=True, resource="Speer", length=4),
                dict(name="Pause_4", length=3),
                dict(name="1500m", together=True, resource="Läufe", length=3),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "is_last_wettkampf_of_the_day": True,
            "plot_color": "red",

        },
        "U14W_5K": {
            "disziplinen": [
                dict(name="60m", together=True, resource="Läufe", length=3),
                dict(name="Pause_1", length=1),
                dict(name="Weit", resource="Weit", length=3),
                dict(name="Pause_2", length=1),
                dict(name="Kugel", resource="Kugel", length=2),
                dict(name="Pause_3", length=1),
                dict(name="Hoch", resource="Hoch", length=3),
                dict(name="Pause_4", length=1),
                dict(name="600m", together=True, resource="Läufe", length=3),
            ],
            "plot_color": "pink",
        },
        "WOM_7K": {
            "disziplinen": [
                dict(name="Weit", together=True, resource="Weit1&Weit2", use_num_anlagen=2, length=4),  # auf Weit1 und Weit2
                dict(name="Pause_1", length=3),
                dict(name="Speer", resource="Speer", length=4),
                dict(name="Pause_2", length=3),
                dict(name="800m", together=True, resource="Läufe", length=4),
            ],
            "is_wettkampf_with_strict_sequence": True,
            "plot_color": "lightgreen",
        },
    }
}

wettkampf_start_times = {
    "saturday": {
        "WOM_7K_Gr1_to_Gr2_100mHü": 9,
        "MAN_10K_Gr22_to_Gr23_100m": 9,
    },
    "sunday": {
        "WOM_7K_Gr1_to_Gr2_Weit": 9,
        "MAN_10K_Gr22_to_Gr23_110mHü": 9,
    },
}

teilnehmer_data = {
    "WOM_7K": {
        "Gr1": 7,
        "Gr2": 16,
    },
    "U16W_5K": {
        "Gr3": 11,
        "Gr4": 11,
        "Gr5": 11,
    },
    "U14W_5K": {
        "Gr6": 12,
        "Gr7": 12,
        "Gr8": 12,
        "Gr9": 12,
        "Gr10": 12,
        "Gr11": 12,
        "Gr12": 12,
    },
    "U12W_4K": {
        "Gr13": 12,
        "Gr14": 12,
        "Gr15": 12,
        "Gr16": 12,
        "Gr17": 12,
        "Gr18": 12,
    },
    "WOM_5K": {
        "Gr19": 7,
        "Gr20": 16,
        "Gr21": 13,
    },
    "MAN_10K": {
        "Gr22": 11,
        "Gr23": 11,
    },
    "U16M_6K": {
        "Gr24": 13,
        "Gr25": 13,
    },
    "U14M_5K": {
        "Gr26": 12,
        "Gr27": 12,
        "Gr28": 12,
        "Gr29": 12,
        "Gr30": 12,
    },
    "U12M_4K": {
        "Gr31": 12,
        "Gr32": 12,
        "Gr33": 12,
        "Gr34": 12,
        "Gr35": 12,
    },
    "MAN_6K": {
        "Gr36": 10,
        "Gr37": 10,
        "Gr38": 10,
        "Gr39": 12,
    },
}

maximum_wettkampf_duration = {
    "saturday": {
        "U12W_4K": 27,
        "U16W_5K": 29,
        "WOM_7K": 26,
        "U12M_4K": 27,
        "U16M_6K": 39,
        "MAN_10K": 33,
    },
    "sunday": {
        "U14W_5K": 31,
        "WOM_7K": 18,
        "WOM_5K": 28,
        "U14M_5K": 26,
        "MAN_10K": 39,
        "MAN_6K": 41,
    },
}


def setup_logging(verbose, event_name):
    log_level = logging.INFO
    if verbose:
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


def main(args):
    start_time = datetime.datetime.now()
    scriptname_without_extension = os.path.splitext(os.path.basename(__file__))[0]
    event_name = "{}_{}".format(scriptname_without_extension, args.day)
    output_folder_name = "{}_{}_{}_{}".format(
        start_time.isoformat(timespec="seconds"), event_name, args.horizon, args.time_limit)
    output_folder_path = os.path.join("results", output_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)
    link_path = os.path.join("results", "latest")
    if os.path.lexists(link_path):
        os.remove(link_path)
    os.symlink(output_folder_name, link_path)
    os.chdir(output_folder_path)

    setup_logging(args.verbose, event_name)

    logging.debug("arguments: {}".format(args))
    logging.debug('output folder: {!r}'.format(output_folder_name))

    event = athletics_event.AthleticsEventScheduler(
        name=event_name, duration_in_units=args.horizon)
    event.create_anlagen(anlagen_descriptors[args.day])
    event.create_disziplinen(
        wettkampf_data[args.day],
        teilnehmer_data,
        maximum_wettkampf_duration=maximum_wettkampf_duration[args.day],
        alternative_objective=args.fast)
    if not args.dont_set_start_time:
        event.set_wettkampf_start_times(wettkampf_start_times[args.day])
    event.ensure_last_wettkampf_of_the_day()
    scenario_as_string = str(event.scenario)
    scenario_filename = '{}_scenario.txt'.format(event_name)
    with open(scenario_filename, 'w') as f:
        f.write(scenario_as_string)
    if args.print_scenario_and_exit:
        logging.info("scenario: {}".format(scenario_as_string))
        sys.exit()
    logging.debug("scenario: {}".format(scenario_as_string))

    if args.time_limit.endswith('s'):
        time_limit_in_secs = float(args.time_limit[:-1])
    elif args.time_limit.endswith('m'):
        time_limit_in_secs = float(args.time_limit[:-1]) * 60
    elif args.time_limit.endswith('h'):
        time_limit_in_secs = float(args.time_limit[:-1]) * 3600
    else:
        time_limit_in_secs = float(args.time_limit)

    try:
        if not args.with_ortools:
            event.solve(time_limit=time_limit_in_secs, ratio_gap=args.ratio_gap, random_seed=args.random_seed, threads=args.threads)
        else:
            event.solve_with_ortools(time_limit=time_limit_in_secs)
    except athletics_event.NoSolutionError as e:
        logging.error("Exception caught: {}".format(e.__class__.__name__))
    logging.info('output folder: {!r}'.format(output_folder_name))
    logging.debug("done")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='calculate event timetable')
    parser.add_argument('--print-scenario-and-exit', action="store_true",
                        help='print scenario and exit')
    default_arguments = {
        "time_limit": "10m",
        "ratio_gap": 0.0,
        "random_seed": None,
        "threads": None,
        "horizon": 54,
    }
    parser.add_argument('-v', '--verbose', action="store_true", help="be verbose")
    help_text = 'time limit, e.g. 30s, 10m, 1h (default: {})'.format(default_arguments["time_limit"])
    parser.add_argument('--time-limit', default=default_arguments["time_limit"], help=help_text)
    help_text = 'ratio gap, e.g. 0.3 (default: {})'.format(default_arguments["ratio_gap"])
    parser.add_argument('--ratio-gap', type=float, default=default_arguments["ratio_gap"], help=help_text)
    help_text = 'random seed, e.g. 42 (default: {})'.format(default_arguments["random_seed"])
    parser.add_argument('--random-seed', type=int, default=default_arguments["random_seed"], help=help_text)
    help_text = 'threads, e.g. 4 (default: {})'.format(default_arguments["threads"])
    parser.add_argument('--threads', type=int, default=default_arguments["threads"], help=help_text)
    parser.add_argument('--dont-set-start-time', action="store_true", help="don't set start time")
    help_text = 'horizon, (default: {})'.format(default_arguments["horizon"])
    parser.add_argument('--horizon', type=int, default=default_arguments["horizon"], help=help_text)
    parser.add_argument('--fast', action="store_true")
    parser.add_argument('--with-ortools', action="store_true")
    valid_wettkampf_days = ['saturday', 'sunday']
    parser.add_argument('day', type=str.lower, choices=valid_wettkampf_days, help='wettkampf day')
    args = parser.parse_args()

    main(args)
