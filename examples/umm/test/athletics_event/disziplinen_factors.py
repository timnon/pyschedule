import unittest

from single_event import BaseEventWithWettkampfHelper


@unittest.skip("outdated")
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
