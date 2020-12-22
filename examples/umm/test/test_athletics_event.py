import logging
import unittest

from athletics_event import AthleticsEventScheduler
import umm2019


logger = logging.getLogger("matplotlib")
logger.setLevel(logging.ERROR)
msg_parameter_for_solver = 1  # 0 (silent) or 1 (verbose)


wettkampf_budget_data = {
    "saturday": {
        # wettkampf: (start_time_unit, end_time_unit)
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


def _getFirstDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data):
    disziplin_name = disziplinen[0]["name"]
    disziplin_length = disziplinen[0]["kwargs"]["length"]
    disziplin_begin = wettkampf_budget_data[wettkampf_name][0]
    disziplin_end = disziplin_begin + disziplin_length
    return "({}_{}_to_{}_{}, {}, {}, {})".format(
        wettkampf_name,
        groups[0],
        groups[-1],
        disziplin_name,
        groups[0],
        disziplin_begin,
        disziplin_end + 1,
    )


def _getLastDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data):
    disziplin_name = disziplinen[-1]["name"]
    disziplin_length = disziplinen[-1]["kwargs"]["length"]
    disziplin_begin = wettkampf_budget_data[wettkampf_name][1]
    disziplin_end = disziplin_begin + disziplin_length
    return "({}_{}_to_{}_{}, {}, {}, {})".format(
        wettkampf_name,
        groups[0],
        groups[-1],
        disziplin_name,
        groups[0],
        disziplin_begin,
        disziplin_end + 1,
    )


class Basics(unittest.TestCase):
    _WETTKAMPF_DAY = "saturday"
    _anlagen_descriptors = [
        ("Läufe",),
        ("Weit", 2),
        ("Kugel", 2),
        ("Hoch", 2),
        ("Diskus",),
    ]
    _wettkampf_budget_data = {
        "U12M_4K": (0, 16),
    }
    _disziplinen_data = {
        "U12M_4K": [
            dict(name="60m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="yellow")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit", sequence_free=True, kwargs=dict(length=3, state=1, plot_color="yellow")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=True, kwargs=dict(length=2, state=1, plot_color="yellow")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="yellow")),
        ],
    }

    def test_instance(self):
        AthleticsEventScheduler(name="test", duration_in_units=1)

    def test_create_anlagen(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=1)
        event.create_anlagen(self._anlagen_descriptors)
        self.assertEqual(str(event.scenario.resources()), "[Läufe, Weit1, Weit2, Kugel1, Kugel2, Hoch1, Hoch2, Diskus]")

    def test_scenario(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=1)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
            },
        }
        event.create_disziplinen(umm2019.disziplinen_data[self._WETTKAMPF_DAY], teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        scenario_as_string = str(event.scenario)
        logging.debug("scenario: {}".format(scenario_as_string))
        expected_scenario_as_string = """
SCENARIO: test / horizon: 1

OBJECTIVE: U12M_4K_Gr30_to_Gr30_60m*-4+U12M_4K_Gr30_Weit+U12M_4K_Gr30_Kugel+U12M_4K_Gr30_to_Gr30_600m*2

RESOURCES:
Läufe
Weit1
Weit2
Kugel1
Kugel2
Hoch1
Hoch2
Diskus
Gr30

TASKS:
U12M_4K_Gr30_to_Gr30_60m : Läufe,Gr30
U12M_4K_Gr30_Weit : Weit1|Weit2,Gr30
U12M_4K_Gr30_Kugel : Kugel1|Kugel2,Gr30
U12M_4K_Gr30_to_Gr30_600m : Läufe,Gr30

JOINT RESOURCES:
Weit1|Weit2 : U12M_4K_Gr30_Weit
Kugel1|Kugel2 : U12M_4K_Gr30_Kugel

LAX PRECEDENCES:
U12M_4K_Gr30_to_Gr30_60m < U12M_4K_Gr30_Weit
U12M_4K_Gr30_to_Gr30_60m < U12M_4K_Gr30_Kugel
U12M_4K_Gr30_to_Gr30_60m < U12M_4K_Gr30_to_Gr30_600m
U12M_4K_Gr30_Weit < U12M_4K_Gr30_to_Gr30_600m
U12M_4K_Gr30_Kugel < U12M_4K_Gr30_to_Gr30_600m
"""
        self.assertIn(expected_scenario_as_string, scenario_as_string)

    def test_solution_and_objective(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        logging.info("scenario: {}".format(str(event._scenario)))
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 32)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr30_60m*-4+U12M_4K_Gr30_Weit+U12M_4K_Gr30_Kugel+U12M_4K_Gr30_to_Gr30_600m*2", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr30_60m, Gr30, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_60m, Läufe, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_600m, Gr30, 27, 31)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_600m, Läufe, 27, 31)", solution_as_string)

    def test_solution_and_objective_in_event_with_two_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 64)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr31_60m*-8+U12M_4K_Gr30_Weit+U12M_4K_Gr30_Kugel+U12M_4K_Gr30_to_Gr31_600m*4+U12M_4K_Gr31_Weit+U12M_4K_Gr31_Kugel", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Gr30, 6, 10)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Gr31, 6, 10)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Läufe, 6, 10)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Gr30, 17, 21)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Gr31, 17, 21)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Läufe, 17, 21)", solution_as_string)

    def test_solution_and_objective_in_event_with_four_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
                "Gr32": 12,
                "Gr33": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 140)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr33_60m*-16+U12M_4K_Gr30_Weit+U12M_4K_Gr30_Kugel+U12M_4K_Gr30_to_Gr33_600m*8+U12M_4K_Gr31_Weit+U12M_4K_Gr31_Kugel+U12M_4K_Gr32_Weit+U12M_4K_Gr32_Kugel+U12M_4K_Gr33_Weit+U12M_4K_Gr33_Kugel", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr30, 3, 7)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr31, 3, 7)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr32, 3, 7)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr33, 3, 7)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Läufe, 3, 7)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr30, 15, 19)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr31, 15, 19)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr32, 15, 19)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr33, 15, 19)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Läufe, 15, 19)", solution_as_string)

    def test_solution_and_objective_in_event_with_six_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
                "Gr32": 12,
                "Gr33": 12,
                "Gr34": 12,
                "Gr35": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 276)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr35_60m*-24+U12M_4K_Gr30_Weit+U12M_4K_Gr30_Kugel+U12M_4K_Gr30_to_Gr35_600m*12+U12M_4K_Gr31_Weit+U12M_4K_Gr31_Kugel+U12M_4K_Gr32_Weit+U12M_4K_Gr32_Kugel+U12M_4K_Gr33_Weit+U12M_4K_Gr33_Kugel+U12M_4K_Gr34_Weit+U12M_4K_Gr34_Kugel+U12M_4K_Gr35_Weit+U12M_4K_Gr35_Kugel", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr30, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr31, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr32, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr33, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr34, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr35, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Läufe, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr30, 36, 40)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr31, 36, 40)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr32, 36, 40)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr33, 36, 40)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr34, 36, 40)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr35, 36, 40)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Läufe, 36, 40)", solution_as_string)

    def test_solution_and_objective_in_event_with_seven_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
                "Gr32": 12,
                "Gr33": 12,
                "Gr34": 12,
                "Gr35": 12,
                "Gr36": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.solve(time_limit=120, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 392)
        objective_as_string = str(event.scenario.objective())
        self.assertEqual("U12M_4K_Gr30_to_Gr36_60m*-28+U12M_4K_Gr30_Weit+U12M_4K_Gr30_Kugel+U12M_4K_Gr30_to_Gr36_600m*14+U12M_4K_Gr31_Weit+U12M_4K_Gr31_Kugel+U12M_4K_Gr32_Weit+U12M_4K_Gr32_Kugel+U12M_4K_Gr33_Weit+U12M_4K_Gr33_Kugel+U12M_4K_Gr34_Weit+U12M_4K_Gr34_Kugel+U12M_4K_Gr35_Weit+U12M_4K_Gr35_Kugel+U12M_4K_Gr36_Weit+U12M_4K_Gr36_Kugel", objective_as_string)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr30, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr31, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr32, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr33, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr34, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr35, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr36, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Läufe, 21, 25)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr30, 41, 45)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr31, 41, 45)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr32, 41, 45)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr33, 41, 45)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr34, 41, 45)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr35, 41, 45)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr36, 41, 45)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Läufe, 41, 45)", solution_as_string)


class BaseEventWithWettkampfHelper(unittest.TestCase):
    _SATURDAY = "saturday"
    _SUNDAY = "sunday"

    def wettkampf_helper(self, wettkampf_budget_data, wettkampf_day, last_wettkampf_of_the_day=None, time_limit=120, objective_override_disziplinen_factors=None):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
        teilnehmer_data = { wettkampf_name: umm2019.teilnehmer_data[wettkampf_name] for wettkampf_name in wettkampf_budget_data }
        event.prepare(
            anlagen_descriptors=umm2019.anlagen_descriptors[wettkampf_day],
            disziplinen_data=umm2019.disziplinen_data[wettkampf_day],
            teilnehmer_data=teilnehmer_data,
            wettkampf_start_times=umm2019.wettkampf_start_times[wettkampf_day])
        if objective_override_disziplinen_factors:
            event.set_objective(objective_override_disziplinen_factors)
        logging.debug("objective: {}".format(event.scenario.objective()))

        if last_wettkampf_of_the_day:
            event.ensure_last_wettkampf_of_the_day(last_wettkampf_of_the_day)
        logging.info("scenario: {}".format(event._scenario))
        event.solve(time_limit=time_limit, msg=msg_parameter_for_solver)
        logging.debug("objective_value: {}".format(event.scenario.objective_value()))

        solution_as_string = str(event.scenario.solution())
        for wettkampf_name in wettkampf_budget_data:
            groups = event.getGroups(wettkampf_name)
            disziplinen = event.getDisziplinen(wettkampf_name)
            expected_first_disziplin_as_string = _getFirstDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_first_disziplin_as_string, solution_as_string)
            expected_last_disziplin_as_string = _getLastDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_last_disziplin_as_string, solution_as_string)
        self.event = event


class OrtoolsBaseEventWithWettkampfHelper(BaseEventWithWettkampfHelper):
    def wettkampf_helper(self, wettkampf_budget_data, wettkampf_day, last_wettkampf_of_the_day=None, time_limit=120, objective_override_disziplinen_factors=None):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
        teilnehmer_data = { wettkampf_name: umm2019.teilnehmer_data[wettkampf_name] for wettkampf_name in wettkampf_budget_data }
        event.prepare(
            anlagen_descriptors=umm2019.anlagen_descriptors[wettkampf_day],
            disziplinen_data=umm2019.disziplinen_data[wettkampf_day],
            teilnehmer_data=teilnehmer_data,
            wettkampf_start_times=umm2019.wettkampf_start_times[wettkampf_day])
        if objective_override_disziplinen_factors:
            event.set_objective(objective_override_disziplinen_factors)
        logging.debug("objective: {}".format(event.scenario.objective()))

        if last_wettkampf_of_the_day:
            event.ensure_last_wettkampf_of_the_day(last_wettkampf_of_the_day)
        event.solve_with_ortools(time_limit=time_limit, msg=msg_parameter_for_solver)
        logging.debug("objective_value: {}".format(event.scenario.objective_value()))

        solution_as_string = str(event.scenario.solution())
        for wettkampf_name in wettkampf_budget_data:
            groups = event.getGroups(wettkampf_name)
            disziplinen = event.getDisziplinen(wettkampf_name)
            expected_first_disziplin_as_string = _getFirstDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_first_disziplin_as_string, solution_as_string)
            expected_last_disziplin_as_string = _getLastDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_last_disziplin_as_string, solution_as_string)
        self.event = event


class OneEventWithStrictSequence(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_saturday(self):
        wettkampf_budget_data = {
           "WOM_7K" : (32, 50),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_sunday(self):
        wettkampf_budget_data = {
            "WOM_7K": (24, 39),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SUNDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16M_6K(self):
        wettkampf_budget_data = {
            "U16M_6K": (20, 51),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_MAN_10K_saturday(self):
        wettkampf_budget_data = {
            "MAN_10K": (33, 59),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_MAN_10K_sunday(self):
        wettkampf_budget_data = {
            "MAN_10K": (14, 46),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SUNDAY)


class OrtoolsOneEventWithStrictSequence(OrtoolsBaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_saturday(self):
        wettkampf_budget_data = {
           "WOM_7K" : (9, 27),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)


class OneEventWithRandomSequence(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K(self):
        wettkampf_budget_data = {
            "U12W_4K": (21, 41),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16W_5K(self):
        wettkampf_budget_data = {
            "U16W_5K": (3, 19),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12M_4K(self):
        wettkampf_budget_data = {
            "U12M_4K": (28, 44),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)


class MoreEvents(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_and_U16M_6K_and_MAN_10K(self):
        wettkampf_budget_data = {
            "U16M_6K": (9, 40),
            "WOM_7K": (12, 30),
            "MAN_10K": (33, 59),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16W_5K_and_WOM_7K_and_U16M_6K_and_MAN_10K(self):
        wettkampf_budget_data = {
            "U16M_6K": (25, 56),
            "WOM_7K": (15, 33),
            "U16W_5K": (3, 19),
            "MAN_10K": (12, 59),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, last_wettkampf_of_the_day="MAN_10K")


class MoreEventsFiddleWithDisziplinenFactors(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_1(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 59),  # +17
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": -1,
            "U12W_4K_Gr14_to_Gr20_600m": 1,
            "U12M_4K_Gr30_to_Gr34_60m": -1,
            "U12M_4K_Gr30_to_Gr34_600m": 1,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_2(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 47),  # +5
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": -1,
            "U12W_4K_Gr14_to_Gr20_600m": 2,
            "U12M_4K_Gr30_to_Gr34_60m": -1,
            "U12M_4K_Gr30_to_Gr34_600m": 2,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)
        # Even increasing time_limit from 120 to 600 does not improve the solution!

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_3(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 43),  # +1
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": -11,
            "U12W_4K_Gr14_Weit": 3,
            "U12W_4K_Gr14_Kugel": 2,
            "U12W_4K_Gr15_Weit": 3,
            "U12W_4K_Gr15_Kugel": 2,
            "U12W_4K_Gr16_Weit": 3,
            "U12W_4K_Gr16_Kugel": 2,
            "U12W_4K_Gr17_Weit": 3,
            "U12W_4K_Gr17_Kugel": 2,
            "U12W_4K_Gr18_Weit": 3,
            "U12W_4K_Gr18_Kugel": 2,
            "U12W_4K_Gr19_Weit": 3,
            "U12W_4K_Gr19_Kugel": 2,
            "U12W_4K_Gr20_Weit": 3,
            "U12W_4K_Gr20_Kugel": 2,
            "U12W_4K_Gr14_to_Gr20_600m": 6,
            "U12M_4K_Gr30_to_Gr34_60m": -11,
            "U12M_4K_Gr30_Weit": 3,
            "U12M_4K_Gr30_Kugel": 2,
            "U12M_4K_Gr31_Weit": 3,
            "U12M_4K_Gr31_Kugel": 2,
            "U12M_4K_Gr32_Weit": 3,
            "U12M_4K_Gr32_Kugel": 2,
            "U12M_4K_Gr33_Weit": 3,
            "U12M_4K_Gr33_Kugel": 2,
            "U12M_4K_Gr34_Weit": 3,
            "U12M_4K_Gr34_Kugel": 2,
            "U12M_4K_Gr30_to_Gr34_600m": 6,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 42),
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": -13,
            "U12W_4K_Gr14_Weit": 6,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 6,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 6,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 6,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 6,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 6,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 6,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 4,
            "U12M_4K_Gr30_to_Gr34_60m": -11,
            "U12M_4K_Gr30_Weit": 6,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 6,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 6,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 6,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 6,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 2,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_2(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 18),  # +2
            "U12W_4K": (22, 43),  # +1
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 5 * 7,
            "U12W_4K_Gr14_Weit": 4,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 4,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 4,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 4,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 4,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 4,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 4,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 2 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 5 * 5,
            "U12M_4K_Gr30_Weit": 4,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 4,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 4,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 4,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 4,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 2 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_3(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 17),  # +1
            "U12W_4K": (22, 49),  # +7
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 5 * 7,
            "U12W_4K_Gr14_Weit": 4,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 4,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 4,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 4,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 4,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 4,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 4,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 1 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 5 * 5,
            "U12M_4K_Gr30_Weit": 4,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 4,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 4,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 4,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 4,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 1 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_4(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),  # +0
            "U12W_4K": (22, 42),  # +0
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 5 * 7,
            "U12W_4K_Gr14_Weit": 4,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 4,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 4,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 4,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 4,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 4,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 4,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 3 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 5 * 5,
            "U12M_4K_Gr30_Weit": 4,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 4,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 4,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 4,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 4,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 3 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_5(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 18),  # +2
            "U12W_4K": (22, 52),  # +10
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 5 * 7,
            "U12W_4K_Gr14_Weit": 3,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 3,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 3,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 3,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 3,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 3,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 3,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 3 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 5 * 5,
            "U12M_4K_Gr30_Weit": 3,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 3,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 3,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 3,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 3,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 3 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_6(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),  # no solution
            "U12W_4K": (22, 42),  # no solution
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 5 * 7,
            "U12W_4K_Gr14_Weit": 4,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 4,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 4,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 4,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 4,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 4,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 4,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 4 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 5 * 5,
            "U12M_4K_Gr30_Weit": 4,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 4,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 4,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 4,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 4,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 4 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

        # no solution!

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_7(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 18),  # +2
            "U12W_4K": (22, 46),  # +4
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 2 * 7,
            "U12W_4K_Gr14_Weit": 4,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 4,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 4,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 4,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 4,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 4,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 4,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 3 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 2 * 5,
            "U12M_4K_Gr30_Weit": 4,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 4,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 4,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 4,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 4,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 3 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_8(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 18),  # +2
            "U12W_4K": (22, 56),  # +14
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 5 * 7,
            "U12W_4K_Gr14_Weit": 4,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 4,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 4,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 4,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 4,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 4,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 4,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 3 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 10 * 5,
            "U12M_4K_Gr30_Weit": 8,
            "U12M_4K_Gr30_Kugel": 6,
            "U12M_4K_Gr31_Weit": 8,
            "U12M_4K_Gr31_Kugel": 6,
            "U12M_4K_Gr32_Weit": 8,
            "U12M_4K_Gr32_Kugel": 6,
            "U12M_4K_Gr33_Weit": 8,
            "U12M_4K_Gr33_Kugel": 6,
            "U12M_4K_Gr34_Weit": 8,
            "U12M_4K_Gr34_Kugel": 6,
            "U12M_4K_Gr30_to_Gr34_600m": 6 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_9(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),  # +0
            "U12W_4K": (22, 43),  # +1
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 10 * 7,
            "U12W_4K_Gr14_Weit": 8,
            "U12W_4K_Gr14_Kugel": 6,
            "U12W_4K_Gr15_Weit": 8,
            "U12W_4K_Gr15_Kugel": 6,
            "U12W_4K_Gr16_Weit": 8,
            "U12W_4K_Gr16_Kugel": 6,
            "U12W_4K_Gr17_Weit": 8,
            "U12W_4K_Gr17_Kugel": 6,
            "U12W_4K_Gr18_Weit": 8,
            "U12W_4K_Gr18_Kugel": 6,
            "U12W_4K_Gr19_Weit": 8,
            "U12W_4K_Gr19_Kugel": 6,
            "U12W_4K_Gr20_Weit": 8,
            "U12W_4K_Gr20_Kugel": 6,
            "U12W_4K_Gr14_to_Gr20_600m": 6 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 5 * 5,
            "U12M_4K_Gr30_Weit": 4,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 4,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 4,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 4,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 4,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 3 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_4_10(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),  # +0
            "U12W_4K": (22, 42),  # +0
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": 15 * 7,
            "U12W_4K_Gr14_Weit": 12,
            "U12W_4K_Gr14_Kugel": 9,
            "U12W_4K_Gr15_Weit": 12,
            "U12W_4K_Gr15_Kugel": 9,
            "U12W_4K_Gr16_Weit": 12,
            "U12W_4K_Gr16_Kugel": 9,
            "U12W_4K_Gr17_Weit": 12,
            "U12W_4K_Gr17_Kugel": 9,
            "U12W_4K_Gr18_Weit": 12,
            "U12W_4K_Gr18_Kugel": 9,
            "U12W_4K_Gr19_Weit": 12,
            "U12W_4K_Gr19_Kugel": 9,
            "U12W_4K_Gr20_Weit": 12,
            "U12W_4K_Gr20_Kugel": 9,
            "U12W_4K_Gr14_to_Gr20_600m": 9 * 7,
            "U12M_4K_Gr30_to_Gr34_60m": 5 * 5,
            "U12M_4K_Gr30_Weit": 4,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 4,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 4,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 4,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 4,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 3 * 5,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_5(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),  # +0
            "U12W_4K": (22, 54),  # +22
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": -11,
            "U12W_4K_Gr14_Weit": 6,
            "U12W_4K_Gr14_Kugel": 3,
            "U12W_4K_Gr15_Weit": 6,
            "U12W_4K_Gr15_Kugel": 3,
            "U12W_4K_Gr16_Weit": 6,
            "U12W_4K_Gr16_Kugel": 3,
            "U12W_4K_Gr17_Weit": 6,
            "U12W_4K_Gr17_Kugel": 3,
            "U12W_4K_Gr18_Weit": 6,
            "U12W_4K_Gr18_Kugel": 3,
            "U12W_4K_Gr19_Weit": 6,
            "U12W_4K_Gr19_Kugel": 3,
            "U12W_4K_Gr20_Weit": 6,
            "U12W_4K_Gr20_Kugel": 3,
            "U12W_4K_Gr14_to_Gr20_600m": 2,
            "U12M_4K_Gr30_to_Gr34_60m": -11,
            "U12M_4K_Gr30_Weit": 6,
            "U12M_4K_Gr30_Kugel": 3,
            "U12M_4K_Gr31_Weit": 6,
            "U12M_4K_Gr31_Kugel": 3,
            "U12M_4K_Gr32_Weit": 6,
            "U12M_4K_Gr32_Kugel": 3,
            "U12M_4K_Gr33_Weit": 6,
            "U12M_4K_Gr33_Kugel": 3,
            "U12M_4K_Gr34_Weit": 6,
            "U12M_4K_Gr34_Kugel": 3,
            "U12M_4K_Gr30_to_Gr34_600m": 2,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_6(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 40),  # +24
            "U12W_4K": (22, 56),  # +14
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": -77,
            "U12W_4K_Gr14_Weit": 1,
            "U12W_4K_Gr14_Kugel": 1,
            "U12W_4K_Gr15_Weit": 1,
            "U12W_4K_Gr15_Kugel": 1,
            "U12W_4K_Gr16_Weit": 1,
            "U12W_4K_Gr16_Kugel": 1,
            "U12W_4K_Gr17_Weit": 1,
            "U12W_4K_Gr17_Kugel": 1,
            "U12W_4K_Gr18_Weit": 1,
            "U12W_4K_Gr18_Kugel": 1,
            "U12W_4K_Gr19_Weit": 1,
            "U12W_4K_Gr19_Kugel": 1,
            "U12W_4K_Gr20_Weit": 1,
            "U12W_4K_Gr20_Kugel": 1,
            "U12W_4K_Gr14_to_Gr20_600m": 63,
            "U12M_4K_Gr30_to_Gr34_60m": -60,
            "U12M_4K_Gr30_Weit": 1,
            "U12M_4K_Gr30_Kugel": 1,
            "U12M_4K_Gr31_Weit": 1,
            "U12M_4K_Gr31_Kugel": 1,
            "U12M_4K_Gr32_Weit": 1,
            "U12M_4K_Gr32_Kugel": 1,
            "U12M_4K_Gr33_Weit": 1,
            "U12M_4K_Gr33_Kugel": 1,
            "U12M_4K_Gr34_Weit": 1,
            "U12M_4K_Gr34_Kugel": 1,
            "U12M_4K_Gr30_to_Gr34_600m": 50,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K_and_U12M_4K_6_2(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),  # +0
            "U12W_4K": (22, 45),  # +3
        }
        disziplinen_factors = {
            "U12W_4K_Gr14_to_Gr20_60m": -77,
            "U12W_4K_Gr14_Weit": 1,
            "U12W_4K_Gr14_Kugel": 1,
            "U12W_4K_Gr15_Weit": 1,
            "U12W_4K_Gr15_Kugel": 1,
            "U12W_4K_Gr16_Weit": 1,
            "U12W_4K_Gr16_Kugel": 1,
            "U12W_4K_Gr17_Weit": 1,
            "U12W_4K_Gr17_Kugel": 1,
            "U12W_4K_Gr18_Weit": 1,
            "U12W_4K_Gr18_Kugel": 1,
            "U12W_4K_Gr19_Weit": 1,
            "U12W_4K_Gr19_Kugel": 1,
            "U12W_4K_Gr20_Weit": 1,
            "U12W_4K_Gr20_Kugel": 1,
            "U12W_4K_Gr14_to_Gr20_600m": 63,
            "U12M_4K_Gr30_to_Gr34_60m": -60,
            "U12M_4K_Gr30_Weit": 1,
            "U12M_4K_Gr30_Kugel": 1,
            "U12M_4K_Gr31_Weit": 1,
            "U12M_4K_Gr31_Kugel": 1,
            "U12M_4K_Gr32_Weit": 1,
            "U12M_4K_Gr32_Kugel": 1,
            "U12M_4K_Gr33_Weit": 1,
            "U12M_4K_Gr33_Kugel": 1,
            "U12M_4K_Gr34_Weit": 1,
            "U12M_4K_Gr34_Kugel": 1,
            "U12M_4K_Gr30_to_Gr34_600m": 50,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors, time_limit=600)


    def test_scheduling_of_first_and_last_disziplin_for_saturday_1(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 42),
            "U16M_6K": (6, 37),
            "WOM_7K": (9, 27),
            "MAN_10K": (20, 46),
        }
        disziplinen_factors = {
            "U12M_4K_Gr30_to_Gr34_60m": 11 * 5 * 5,
            "U12M_4K_Gr30_Weit": 11 * 4,
            "U12M_4K_Gr30_Kugel": 11 * 3,
            "U12M_4K_Gr31_Weit": 11 * 4,
            "U12M_4K_Gr31_Kugel": 11 * 3,
            "U12M_4K_Gr32_Weit": 11 * 4,
            "U12M_4K_Gr32_Kugel": 11 * 3,
            "U12M_4K_Gr33_Weit": 11 * 4,
            "U12M_4K_Gr33_Kugel": 11 * 3,
            "U12M_4K_Gr34_Weit": 11 * 4,
            "U12M_4K_Gr34_Kugel": 11 * 3,
            "U12M_4K_Gr30_to_Gr34_600m": 11 * 3 * 5,

            "U12W_4K_Gr14_to_Gr20_60m": 2 * 5 * 7,
            "U12W_4K_Gr14_Weit": 2 * 4,
            "U12W_4K_Gr14_Kugel": 2 * 3,
            "U12W_4K_Gr15_Weit": 2 * 4,
            "U12W_4K_Gr15_Kugel": 2 * 3,
            "U12W_4K_Gr16_Weit": 2 * 4,
            "U12W_4K_Gr16_Kugel": 2 * 3,
            "U12W_4K_Gr17_Weit": 2 * 4,
            "U12W_4K_Gr17_Kugel": 2 * 3,
            "U12W_4K_Gr18_Weit": 2 * 4,
            "U12W_4K_Gr18_Kugel": 2 * 3,
            "U12W_4K_Gr19_Weit": 2 * 4,
            "U12W_4K_Gr19_Kugel": 2 * 3,
            "U12W_4K_Gr20_Weit": 2 * 4,
            "U12W_4K_Gr20_Kugel": 2 * 3,
            "U12W_4K_Gr14_to_Gr20_600m": 2 * 3 * 7,

            "U16M_6K_Gr24_to_Gr25_100mHü": 7 * 8 * 2,
            "U16M_6K_Gr24_Weit": 7 * 7,
            "U16M_6K_Gr24_Kugel": 7 * 6,
            "U16M_6K_Gr24_Hoch": 7 * 5,
            "U16M_6K_Gr25_Weit": 7 * 7,
            "U16M_6K_Gr25_Kugel": 7 * 6,
            "U16M_6K_Gr25_Hoch": 7 * 5,
            "U16M_6K_Gr24_to_Gr25_Diskus": 7 * 4,
            "U16M_6K_Gr24_to_Gr25_1000m": 7 * 3 * 2,

            "WOM_7K_Gr1_to_Gr2_100mHü": 12 * 5 * 2,
            "WOM_7K_Gr1_Hoch": 12 * 4,
            "WOM_7K_Gr1_Kugel": 12 * 3,
            "WOM_7K_Gr2_Hoch": 12 * 4,
            "WOM_7K_Gr2_Kugel": 12 * 3,
            "WOM_7K_Gr1_to_Gr2_200m": 12 * 3 * 2,

            "MAN_10K_Gr23_to_Gr23_100m": 11 * 7,
            "MAN_10K_Gr23_Weit": 11 * 6,
            "MAN_10K_Gr23_Kugel": 11 * 5,
            "MAN_10K_Gr23_Hoch": 11 * 4,
            "MAN_10K_Gr23_to_Gr23_400m": 11 * 3,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors, time_limit=600)

    def test_scheduling_of_first_and_last_disziplin_for_saturday_2(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 42),
            "U16M_6K": (6, 37),
            "U16W_5K": (13, 42),
            "WOM_7K": (9, 27),
            "MAN_10K": (20, 46),
        }
        disziplinen_factors = {
            "U12M_4K_Gr30_to_Gr34_60m": 11 * 5 * 5,
            "U12M_4K_Gr30_Weit": 11 * 4,
            "U12M_4K_Gr30_Kugel": 11 * 3,
            "U12M_4K_Gr31_Weit": 11 * 4,
            "U12M_4K_Gr31_Kugel": 11 * 3,
            "U12M_4K_Gr32_Weit": 11 * 4,
            "U12M_4K_Gr32_Kugel": 11 * 3,
            "U12M_4K_Gr33_Weit": 11 * 4,
            "U12M_4K_Gr33_Kugel": 11 * 3,
            "U12M_4K_Gr34_Weit": 11 * 4,
            "U12M_4K_Gr34_Kugel": 11 * 3,
            "U12M_4K_Gr30_to_Gr34_600m": 11 * 3 * 5,

            "U12W_4K_Gr14_to_Gr20_60m": 2 * 5 * 7,
            "U12W_4K_Gr14_Weit": 2 * 4,
            "U12W_4K_Gr14_Kugel": 2 * 3,
            "U12W_4K_Gr15_Weit": 2 * 4,
            "U12W_4K_Gr15_Kugel": 2 * 3,
            "U12W_4K_Gr16_Weit": 2 * 4,
            "U12W_4K_Gr16_Kugel": 2 * 3,
            "U12W_4K_Gr17_Weit": 2 * 4,
            "U12W_4K_Gr17_Kugel": 2 * 3,
            "U12W_4K_Gr18_Weit": 2 * 4,
            "U12W_4K_Gr18_Kugel": 2 * 3,
            "U12W_4K_Gr19_Weit": 2 * 4,
            "U12W_4K_Gr19_Kugel": 2 * 3,
            "U12W_4K_Gr20_Weit": 2 * 4,
            "U12W_4K_Gr20_Kugel": 2 * 3,
            "U12W_4K_Gr14_to_Gr20_600m": 2 * 3 * 7,

            "U16M_6K_Gr24_to_Gr25_100mHü": 7 * 8 * 2,
            "U16M_6K_Gr24_Weit": 7 * 7,
            "U16M_6K_Gr24_Kugel": 7 * 6,
            "U16M_6K_Gr24_Hoch": 7 * 5,
            "U16M_6K_Gr25_Weit": 7 * 7,
            "U16M_6K_Gr25_Kugel": 7 * 6,
            "U16M_6K_Gr25_Hoch": 7 * 5,
            "U16M_6K_Gr24_to_Gr25_Diskus": 7 * 4,
            "U16M_6K_Gr24_to_Gr25_1000m": 7 * 3 * 2,

            "U16W_5K_Gr3_to_Gr6_80m": 3 * 6 * 4,
            "U16W_5K_Gr3_Weit": 3 * 5,
            "U16W_5K_Gr3_Kugel": 3 * 4,
            "U16W_5K_Gr3_Hoch": 3 * 3,
            "U16W_5K_Gr4_Weit": 3 * 5,
            "U16W_5K_Gr4_Kugel": 3 * 4,
            "U16W_5K_Gr4_Hoch": 3 * 3,
            "U16W_5K_Gr5_Weit": 3 * 5,
            "U16W_5K_Gr5_Kugel": 3 * 4,
            "U16W_5K_Gr5_Hoch": 3 * 3,
            "U16W_5K_Gr6_Weit": 3 * 5,
            "U16W_5K_Gr6_Kugel": 3 * 4,
            "U16W_5K_Gr6_Hoch": 3 * 3,
            "U16W_5K_Gr3_to_Gr6_600m": 3 * 3 * 4,

            "WOM_7K_Gr1_to_Gr2_100mHü": 12 * 5 * 2,
            "WOM_7K_Gr1_Hoch": 12 * 4,
            "WOM_7K_Gr1_Kugel": 12 * 3,
            "WOM_7K_Gr2_Hoch": 12 * 4,
            "WOM_7K_Gr2_Kugel": 12 * 3,
            "WOM_7K_Gr1_to_Gr2_200m": 12 * 3 * 2,

            "MAN_10K_Gr23_to_Gr23_100m": 11 * 7,
            "MAN_10K_Gr23_Weit": 11 * 6,
            "MAN_10K_Gr23_Kugel": 11 * 5,
            "MAN_10K_Gr23_Hoch": 11 * 4,
            "MAN_10K_Gr23_to_Gr23_400m": 11 * 3,
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY, objective_override_disziplinen_factors=disziplinen_factors, time_limit=3600)


if __name__ == '__main__':
    unittest.main()
