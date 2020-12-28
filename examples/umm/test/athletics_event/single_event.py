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
    disziplin_length = disziplinen[0]["length"]
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
    disziplin_length = disziplinen[-1]["length"]
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


class TwoAndMoreGroups(unittest.TestCase):
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
    }

    def test_solution_and_objective_in_event_with_two_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12M_4K": {
                "Gr30": 12,
                "Gr31": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.solve(time_limit=10, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 68)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Gr30, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Gr31, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_60m, Läufe, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Gr30, 11, 15)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Gr31, 11, 15)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr31_600m, Läufe, 11, 15)", solution_as_string)

    def test_solution_and_objective_in_event_with_four_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
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
        event.solve(time_limit=10, ratio_gap=1, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 144)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr30, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr31, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr32, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Gr33, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_60m, Läufe, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr30, 12, 16)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr31, 12, 16)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr32, 12, 16)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Gr33, 12, 16)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr33_600m, Läufe, 12, 16)", solution_as_string)

    def test_solution_and_objective_in_event_with_six_groups(self):
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
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.solve(time_limit=10, ratio_gap=1, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 280)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr30, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr31, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr32, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr33, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr34, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Gr35, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_60m, Läufe, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr30, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr31, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr32, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr33, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr34, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Gr35, 16, 20)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr35_600m, Läufe, 16, 20)", solution_as_string)

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
        event.solve(time_limit=10, ratio_gap=1, msg=msg_parameter_for_solver)
        self.assertEqual(event.scenario.objective_value(), 403)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr30, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr31, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr32, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr33, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr34, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr35, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Gr36, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_60m, Läufe, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr30, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr31, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr32, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr33, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr34, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr35, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Gr36, 20, 24)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr36_600m, Läufe, 20, 24)", solution_as_string)


class BaseEventWithWettkampfHelper(unittest.TestCase):
    _SATURDAY = "saturday"
    _SUNDAY = "sunday"

    def wettkampf_helper(self, wettkampf_budget_data, wettkampf_day, time_limit=10, objective_override_disziplinen_factors=None):
        event = AthleticsEventScheduler(name="test", duration_in_units=60)
        teilnehmer_data = { wettkampf_name: umm2019.teilnehmer_data[wettkampf_name] for wettkampf_name in wettkampf_budget_data }
        event.prepare(
            anlagen_descriptors=umm2019.anlagen_descriptors[wettkampf_day],
            disziplinen_data=umm2019.wettkampf_data[wettkampf_day],
            teilnehmer_data=teilnehmer_data,
            wettkampf_start_times=umm2019.wettkampf_start_times[wettkampf_day])
        if objective_override_disziplinen_factors:
            event.set_objective(objective_override_disziplinen_factors)
        logging.debug("objective: {}".format(event.scenario.objective()))

        event.ensure_last_wettkampf_of_the_day()
        logging.info("scenario: {}".format(event._scenario))
        event.solve(time_limit=time_limit, ratio_gap=1, msg=msg_parameter_for_solver)

        solution_as_string = str(event.scenario.solution())
        for wettkampf_name in wettkampf_budget_data:
            groups = event.getGroups(wettkampf_name)
            disziplinen = event.getDisziplinen(wettkampf_name)
            expected_first_disziplin_as_string = _getFirstDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_first_disziplin_as_string, solution_as_string)
            expected_last_disziplin_as_string = _getLastDisziplinAsString(wettkampf_name, groups, disziplinen, wettkampf_budget_data)
            self.assertIn(expected_last_disziplin_as_string, solution_as_string)
        self.event = event


class SingleEventWithStrictSequence(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_saturday(self):
        wettkampf_budget_data = {
           "WOM_7K" : (12, 30),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_sunday(self):
        wettkampf_budget_data = {
            "WOM_7K": (12, 27),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SUNDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16M_6K(self):
        wettkampf_budget_data = {
            "U16M_6K": (0, 31),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_MAN_10K_saturday(self):
        wettkampf_budget_data = {
            "MAN_10K": (12, 38),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_MAN_10K_sunday(self):
        wettkampf_budget_data = {
            "MAN_10K": (12, 44),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SUNDAY)


class SingleEventWithRandomSequence(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12W_4K(self):
        wettkampf_budget_data = {
            "U12W_4K": (0, 20),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16W_5K(self):
        wettkampf_budget_data = {
            "U16W_5K": (7, 23),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U12M_4K(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)
