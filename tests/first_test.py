#!/usr/bin/python
# coding: utf-8
import pyschedule


def test_creating_empty_scenario():
    S = pyschedule.Scenario('Empty')
    assert S is not None
