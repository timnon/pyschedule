import logging
import unittest

from athletics_event import AthleticsEventScheduler
import umm2019


logger = logging.getLogger("matplotlib")
logger.setLevel(logging.ERROR)
msg_parameter_for_solver = 1  # 0 (silent) or 1 (verbose)

class TestAnlagenDescriptor(unittest.TestCase):
    _WETTKAMPF_DAY = "saturday"
    _anlagen_descriptors = [
        ("Läufe",),
        ("Weit", 2),
        ("Kugel", 2),
        ("Hoch", 2),
        ("Diskus",),
    ]
    _wettkampf_budget_data = {
        "U12W_4K": (22, 49),
    }
    _disziplinen_data = {
        "U12W_4K": [
            dict(name="60m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="orange")),
            dict(name="Pause_1", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Weit", together=False, resource="Weit", sequence_free=True, kwargs=dict(length=3, state=1, plot_color="orange")),
            dict(name="Pause_2", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="Kugel", together=False, resource="Kugel", sequence_free=True, kwargs=dict(length=2, state=1, plot_color="orange")),
            dict(name="Pause_3", together=False, resource=None, sequence_free=False, kwargs=dict(length=1, state=-1, plot_color='white')),
            dict(name="600m", together=True, resource="Läufe", sequence_free=False, kwargs=dict(length=3, state=1, plot_color="orange")),
        ],
    }
    _teilnehmer_data = {
        "U12W_4K": {
            "Gr14": 13,
        },
    }

    def test_instance(self):
        AthleticsEventScheduler(name="test", duration_in_units=1)

    def test_create_anlagen(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=1)
        event.create_anlagen(self._anlagen_descriptors)
        self.assertEqual(str(event.scenario.resources()), "[Läufe, Weit1, Weit2, Kugel1, Kugel2, Hoch1, Hoch2, Diskus]")

    def test_scenario(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=1, wettkampf_budget_data=self._wettkampf_budget_data)
        event.create_anlagen(self._anlagen_descriptors)
        event.create_disziplinen(self._disziplinen_data, self._teilnehmer_data)
        event.create_anlagen_pausen()
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        scenario_as_string = str(event.scenario)
        expected_scenario_as_string = """
SCENARIO: test / horizon: 1

OBJECTIVE: U12W_4K_Gr14_to_Gr14_60m*-4+U12W_4K_Gr14_to_Gr14_600m*14

RESOURCES:
Läufe
Weit1
Weit2
Kugel1
Kugel2
Hoch1
Hoch2
Diskus
Gr14

TASKS:
U12W_4K_Gr14_to_Gr14_60m : Läufe,Gr14
U12W_4K_Gr14_Pause_1 : Gr14
U12W_4K_Gr14_Weit : Weit1|Weit2,Gr14
U12W_4K_Gr14_Pause_2 : Gr14
U12W_4K_Gr14_Kugel : Kugel1|Kugel2,Gr14
U12W_4K_Gr14_Pause_3 : Gr14
U12W_4K_Gr14_to_Gr14_600m : Läufe,Gr14
Läufe_Pause_1 : Läufe
Läufe_Pause_2 : Läufe
Weit1_Pause_1 : Weit1
Weit2_Pause_1 : Weit2
Kugel1_Pause_1 : Kugel1
Kugel2_Pause_1 : Kugel2

JOINT RESOURCES:
Weit1|Weit2 : U12W_4K_Gr14_Weit
Kugel1|Kugel2 : U12W_4K_Gr14_Kugel

LAX PRECEDENCES:
U12W_4K_Gr14_to_Gr14_60m < U12W_4K_Gr14_Weit
U12W_4K_Gr14_to_Gr14_60m < U12W_4K_Gr14_Kugel
U12W_4K_Gr14_Weit < U12W_4K_Gr14_to_Gr14_600m
U12W_4K_Gr14_Kugel < U12W_4K_Gr14_to_Gr14_600m

CAPACITY BOUNDS:
Gr14['state'][:0] <= 1
-1*Gr14['state'][:0] <= 0
Läufe['state'][:0] <= 1
-1*Läufe['state'][:0] <= 0
Weit1['state'][:0] <= 1
-1*Weit1['state'][:0] <= 0
Weit2['state'][:0] <= 1
-1*Weit2['state'][:0] <= 0
Kugel1['state'][:0] <= 1
-1*Kugel1['state'][:0] <= 0
Kugel2['state'][:0] <= 1
-1*Kugel2['state'][:0] <= 0
Hoch1['state'][:0] <= 1
-1*Hoch1['state'][:0] <= 0
Hoch2['state'][:0] <= 1
-1*Hoch2['state'][:0] <= 0
Diskus['state'][:0] <= 1
-1*Diskus['state'][:0] <= 0
"""
        self.assertIn(expected_scenario_as_string, scenario_as_string)

    def test_solution_and_objective(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40, wettkampf_budget_data=self._wettkampf_budget_data)
        event.create_anlagen(self._anlagen_descriptors)
        event.create_disziplinen(self._disziplinen_data, self._teilnehmer_data)
        event.create_anlagen_pausen()
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event._scenario.objective_value(), 184)
        objective_as_string = str(event._scenario.objective())
        expected_objective_as_string = "U12W_4K_Gr14_to_Gr14_60m*-4+U12W_4K_Gr14_to_Gr14_600m*14"
        self.assertEqual(expected_objective_as_string, objective_as_string)
        solution_as_string = str(event._scenario.solution())
        self.assertIn("(U12W_4K_Gr14_to_Gr14_60m, Gr14, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr14_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr14_600m, Gr14, 11, 14)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr14_600m, Läufe, 11, 14)", solution_as_string)

    def test_solution_and_objective_in_event_with_two_groups(self):
        
        event = AthleticsEventScheduler(name="test", duration_in_units=40, wettkampf_budget_data=self._wettkampf_budget_data)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12W_4K": {
                "Gr14": 13,
                "Gr15": 13,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        event.solve(time_limit=60, ratio_gap=1, random_seed=None, threads=None, msg=msg_parameter_for_solver)
        self.assertEqual(event._scenario.objective_value(), 184)
        objective_as_string = str(event._scenario.objective())
        expected_objective_as_string = "U12W_4K_Gr14_to_Gr15_60m*-4+U12W_4K_Gr14_to_Gr15_600m*14"
        self.assertEqual(expected_objective_as_string, objective_as_string)
        solution_as_string = str(event._scenario.solution())
        self.assertIn("(U12W_4K_Gr14_to_Gr15_60m, Gr14, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr15_60m, Gr15, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr15_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr15_600m, Gr14, 11, 14)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr15_600m, Gr15, 11, 14)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr15_600m, Läufe, 11, 14)", solution_as_string)

    def test_solution_and_objective_in_event_with_four_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40, wettkampf_budget_data=self._wettkampf_budget_data)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12W_4K": {
                "Gr14": 12,
                "Gr15": 12,
                "Gr16": 12,
                "Gr17": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        event.solve(time_limit=60, msg=msg_parameter_for_solver)
        self.assertEqual(event._scenario.objective_value(), 422)
        objective_as_string = str(event._scenario.objective())
        expected_objective_as_string = "U12W_4K_Gr14_to_Gr17_60m*-4+U12W_4K_Gr14_to_Gr17_600m*14"
        self.assertEqual(expected_objective_as_string, objective_as_string)
        solution_as_string = str(event._scenario.solution())
        self.assertIn("(U12W_4K_Gr14_to_Gr17_60m, Gr14, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_60m, Gr15, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_60m, Gr16, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_60m, Gr17, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_600m, Gr14, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_600m, Gr15, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_600m, Gr16, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_600m, Gr17, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr17_600m, Läufe, 28, 31)", solution_as_string)

    def test_solution_and_objective_in_event_with_six_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=40, wettkampf_budget_data=self._wettkampf_budget_data)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12W_4K": {
                "Gr14": 12,
                "Gr15": 12,
                "Gr16": 12,
                "Gr17": 12,
                "Gr18": 12,
                "Gr19": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        event.solve(time_limit=60, ratio_gap=1, random_seed=None, threads=None, msg=msg_parameter_for_solver)
        self.assertEqual(event._scenario.objective_value(), 422)
        objective_as_string = str(event._scenario.objective())
        expected_objective_as_string = "U12W_4K_Gr14_to_Gr20_60m*-4+U12W_4K_Gr14_to_Gr20_600m*14"
        self.assertEqual(expected_objective_as_string, objective_as_string)
        solution_as_string = str(event._scenario.solution())
        self.assertIn("(U12W_4K_Gr14_to_Gr19_60m, Gr14, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_60m, Gr15, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_60m, Gr16, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_60m, Gr17, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_60m, Gr18, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_60m, Gr19, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_600m, Gr14, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_600m, Gr15, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_600m, Gr16, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_600m, Gr17, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_600m, Gr18, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_600m, Gr19, 28, 31)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr19_600m, Läufe, 28, 31)", solution_as_string)

    def test_solution_and_objective_in_event_with_seven_groups(self):
        event = AthleticsEventScheduler(name="test", duration_in_units=60, wettkampf_budget_data=self._wettkampf_budget_data)
        event.create_anlagen(self._anlagen_descriptors)
        teilnehmer_data = {
            "U12W_4K": {
                "Gr14": 12,
                "Gr15": 12,
                "Gr16": 12,
                "Gr17": 12,
                "Gr18": 12,
                "Gr19": 12,
                "Gr20": 12,
            },
        }
        event.create_disziplinen(self._disziplinen_data, teilnehmer_data)
        event.create_anlagen_pausen()
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        event.solve(time_limit=120, ratio_gap=0, msg=msg_parameter_for_solver)
        #self.assertEqual(event._scenario.objective_value(), 26)
        #objective_as_string = str(event._scenario.objective())
        #expected_objective_as_string = "U12W_4K_Gr14_to_Gr20_60m+U12W_4K_Gr14_to_Gr20_600m*2"
        #self.assertEqual(expected_objective_as_string, objective_as_string)
        solution_as_string = str(event._scenario.solution())
        self.assertIn("(U12W_4K_Gr14_to_Gr20_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr20_600m, Läufe, 20, 23)", solution_as_string)


class TestOneEvent(unittest.TestCase):
    _WETTKAMPF_DAY = "saturday"

    def test_solution_and_objective_for_wettkampf_U12M(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
        }
        event = AthleticsEventScheduler(name="test", duration_in_units=60, wettkampf_budget_data=wettkampf_budget_data)
        event.create_anlagen(umm2019.anlagen_descriptors[self._WETTKAMPF_DAY])
        teilnehmer_data = { wettkampf_name: umm2019.teilnehmer_data[wettkampf_name] for wettkampf_name in wettkampf_budget_data }
        event.create_disziplinen(umm2019.disziplinen_data[self._WETTKAMPF_DAY], teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        event.solve(time_limit=120, msg=msg_parameter_for_solver)
        #self.assertEqual(event._scenario.objective_value(), 26)
        #objective_as_string = str(event._scenario.objective())
        #expected_objective_as_string = "U12W_4K_Gr14_to_Gr20_60m+U12W_4K_Gr14_to_Gr20_600m*2"
        #self.assertEqual(expected_objective_as_string, objective_as_string)
        solution_as_string = str(event._scenario.solution())
        self.assertIn("(U12M_4K_Gr30_to_Gr34_60m, Läufe, 0, 3)", solution_as_string)
        self.assertIn("(U12M_4K_Gr30_to_Gr34_600m, Läufe, 16, 19)", solution_as_string)

    def test_solution_and_objective_for_wettkampf_U12W(self):
        wettkampf_budget_data = {
            "U12W_4K": (22, 42),
        }
        event = AthleticsEventScheduler(name="test", duration_in_units=60, wettkampf_budget_data=wettkampf_budget_data)
        event.create_anlagen(umm2019.anlagen_descriptors[self._WETTKAMPF_DAY])
        teilnehmer_data = { wettkampf_name: umm2019.teilnehmer_data[wettkampf_name] for wettkampf_name in wettkampf_budget_data }
        event.create_disziplinen(umm2019.disziplinen_data[self._WETTKAMPF_DAY], teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        event.solve(time_limit=120, msg=msg_parameter_for_solver)
        #self.assertEqual(event._scenario.objective_value(), 26)
        #objective_as_string = str(event._scenario.objective())
        #expected_objective_as_string = "U12W_4K_Gr14_to_Gr20_60m+U12W_4K_Gr14_to_Gr20_600m*2"
        #self.assertEqual(expected_objective_as_string, objective_as_string)
        solution_as_string = str(event._scenario.solution())
        self.assertIn("(U12W_4K_Gr14_to_Gr20_60m, Läufe, 22, 25)", solution_as_string)
        self.assertIn("(U12W_4K_Gr14_to_Gr20_600m, Läufe, 42, 45)", solution_as_string)


class TestTwoEvents(unittest.TestCase):
    _WETTKAMPF_DAY = "saturday"

    def test_solution_and_objective(self):
        wettkampf_budget_data = {
            "U12M_4K": (0, 16),
            "U12W_4K": (22, 42),
        }
        event = AthleticsEventScheduler(name="test", duration_in_units=60, wettkampf_budget_data=wettkampf_budget_data)
        event.create_anlagen(umm2019.anlagen_descriptors[self._WETTKAMPF_DAY])
        teilnehmer_data = { wettkampf_name: umm2019.teilnehmer_data[wettkampf_name] for wettkampf_name in wettkampf_budget_data }
        event.create_disziplinen(umm2019.disziplinen_data[self._WETTKAMPF_DAY], teilnehmer_data)
        event.create_anlagen_pausen()
        event.set_wettkampf_start_times(umm2019.wettkampf_start_times[self._WETTKAMPF_DAY])
        event.ensure_pausen_for_gruppen_and_anlagen()
        event.set_objective()
        logging.info("objective: {}".format(event._scenario.objective()))
        event.solve(time_limit=120, msg=msg_parameter_for_solver)


if __name__ == '__main__':
    unittest.main()
