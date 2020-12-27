import logging
import unittest

from athletics_event import AthleticsEventScheduler
import umm2019


logger = logging.getLogger("matplotlib")
logger.setLevel(logging.ERROR)
msg_parameter_for_solver = 1  # 0 (silent) or 1 (verbose)


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
        event.create_disziplinen(umm2019.wettkampf_data[self._WETTKAMPF_DAY], teilnehmer_data)
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        scenario_as_string = str(event.scenario)
        logging.debug("scenario: {}".format(scenario_as_string))
        expected_scenario_as_string = """
SCENARIO: test / horizon: 1

OBJECTIVE: U12M_4K_Gr30_to_Gr30_60m*-3+U12M_4K_Gr30_Weit+U12M_4K_Gr30_Kugel+U12M_4K_Gr30_to_Gr30_600m*2

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
        self.assertEqual(event.scenario.objective_value(), 36)
        solution_as_string = str(event.scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr30_60m, Gr30, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_60m, Läufe, 0, 4)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_600m, Gr30, 11, 15)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr30_600m, Läufe, 11, 15)", solution_as_string)


if __name__ == '__main__':
    unittest.main()
