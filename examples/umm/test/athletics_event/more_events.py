from single_event import BaseEventWithWettkampfHelper


class MoreEvents(BaseEventWithWettkampfHelper):
    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_WOM_7K_and_U16M_6K_and_MAN_10K(self):
        wettkampf_budget_data = {
            "U16M_6K": (0, 31),
            "WOM_7K": (16, 34),
            "MAN_10K": (12, 38),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)

    def test_scheduling_of_first_and_last_disziplin_for_wettkampf_U16W_5K_and_WOM_7K_and_U16M_6K_and_MAN_10K(self):
        wettkampf_budget_data = {
            "U16M_6K": (5, 36),
            "WOM_7K": (18, 39),
            "U16W_5K": (0, 22),
            "MAN_10K": (16, 42),
        }
        self.wettkampf_helper(wettkampf_budget_data=wettkampf_budget_data, wettkampf_day=self._SATURDAY)
