import logging
import unittest

from single_event import BaseEventWithWettkampfHelper
from single_event import _getFirstDisziplinAsString
from single_event import _getLastDisziplinAsString

from athletics_event import AthleticsEventScheduler
import umm2019


logger = logging.getLogger("matplotlib")
logger.setLevel(logging.ERROR)
msg_parameter_for_solver = 1  # 0 (silent) or 1 (verbose)


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


@unittest.skip("in development")
class OrtoolsOneEventWithStrictSequence(OrtoolsBaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_saturday(self):
        wettkampf_budget_data = {
           "WOM_7K" : (9, 27),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)
