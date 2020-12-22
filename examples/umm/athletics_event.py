import sys
sys.path.append('../../src')

import argparse
from collections import defaultdict
import datetime
import functools
import logging
import operator
import os
from pyschedule import Scenario, solvers, plotters, alt


class NoSolutionError(RuntimeError):
    pass


class AnlagenDescriptor(object):
    def __init__(self, name, size=1):
        self._name = name
        self._size = size

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size


class AthleticsEventScheduler(object):
    def __init__(self, name, duration_in_units):
        self._name = name
        self._duration_in_units = duration_in_units
        self._anlagen = {}
        self._last_disziplin = {}
        self._used_anlagen = defaultdict(int)
        self._disziplinen = {}
        self._hide_tasks = []
        self._sequence_not_strict_gruppen = []
        self.create_scenario()

    def create_scenario(self):
        self._scenario = Scenario(self._name, horizon=self._duration_in_units)

    @property
    def scenario(self):
        return self._scenario

    def prepare(self, anlagen_descriptors, disziplinen_data, teilnehmer_data, wettkampf_start_times):
        self.create_anlagen(anlagen_descriptors)
        self.create_disziplinen(disziplinen_data, teilnehmer_data)
        self.set_wettkampf_start_times(wettkampf_start_times)

    def create_anlagen(self, descriptors):
        logging.debug('creating anlagen...')
        for descriptor in descriptors:
            self._create_anlage(descriptor)

    def _create_anlage(self, descriptor_args):
        descriptor = AnlagenDescriptor(*descriptor_args)
        for i in range(descriptor.size):
            anlagen_name = descriptor.name
            if descriptor.size > 1:
                anlagen_name += "{}".format(i + 1)
            logging.debug("  {}".format(anlagen_name))
            anlage = self._scenario.Resource(anlagen_name)
            self._anlagen[anlagen_name] = anlage

    def any_anlage(self, pattern):
        return functools.reduce(lambda a, b: operator.or_(a, b), self._get_all_anlagen(pattern))

    def _get_all_anlagen(self, pattern):
        resources = []
        for anlagen_name, anlage in self._anlagen.items():
            if anlagen_name.startswith(pattern):
                resources.append(anlage)
        return resources

    def create_disziplinen(self, disziplinen_data, teilnehmer_data):
        self._disziplinen_data = disziplinen_data
        self._teilnehmer_data = teilnehmer_data
        logging.debug('creating disziplinen...')
        for wettkampf_name in disziplinen_data:
            if wettkampf_name not in teilnehmer_data:
                continue
            logging.debug("  wettkampf: {}".format(wettkampf_name))
            gruppen_names = list(teilnehmer_data[wettkampf_name].keys())
            wettkampf_disziplinen_factors = defaultdict(int)
            for gruppen_name in gruppen_names:
                logging.debug("    gruppe: {}".format(gruppen_name))
                gruppe = self._scenario.Resource(gruppen_name)
                gruppen_disziplinen = []
                for item in disziplinen_data[wettkampf_name]:
                    disziplinen_name = "{}_{}_{}".format(wettkampf_name, gruppen_name, item["name"])
                    logging.debug("      disziplin: {}".format(disziplinen_name))
                    if item["together"]:
                        disziplinen_name = "{}_{}_to_{}_{}".format(wettkampf_name, gruppen_names[0], gruppen_names[-1], item["name"])
                    if disziplinen_name not in self._disziplinen.keys():
                        kwargs = item["kwargs"].copy()
                        kwargs['together'] = item["together"]
                        if "pause" not in disziplinen_name.lower():
                            kwargs["length"] += 1
                        else:
                            kwargs["length"] -= 1
                            if kwargs["length"] <= 0:
                                continue
                        disziplin = self._scenario.Task(disziplinen_name, **kwargs)
                        self._disziplinen[disziplinen_name] = disziplin
                    else:
                        disziplin = self._disziplinen[disziplinen_name]
                    gruppen_disziplinen.append(disziplin)

                    if item["resource"]:
                        resource_base_name = item["resource"]
                        resource_names = item["resource"].split("&")
                        if resource_names[0][-1].isdigit():
                            resource_base_name = resource_names[0][:-1]
                        self._used_anlagen[resource_base_name] += 1
                        if not item["together"] or gruppen_name == gruppen_names[0]:
                            for resource_name in resource_names:
                                disziplin += self.any_anlage(resource_name)

                    disziplin += gruppe

                    if "pause" in disziplinen_name.lower():
                        self._hide_tasks.append(disziplin)

                first_disziplin = gruppen_disziplinen[0]
                last_disziplin = gruppen_disziplinen[-1]
                wettkampf_with_pausen = "pause" in gruppen_disziplinen[1]["name"].lower()
                if self._is_wettkampf_disziplinen_sequence_strict(wettkampf_name):
                    # one after another: 1st, 1st-pause, 2nd, 2nd-pause, 3rd,...
                    current_disziplin = gruppen_disziplinen[0]
                    for next_disziplin in gruppen_disziplinen[1:]:
                        self._scenario += current_disziplin < next_disziplin
                        current_disziplin = next_disziplin
                else:
                    # 1st and last set - rest free
                    if wettkampf_with_pausen:
                        # make disziplin-pause pairs
                        for disziplin_index in range(len(gruppen_disziplinen[:-1:2])):
                            self._scenario += gruppen_disziplinen[disziplin_index * 2] < gruppen_disziplinen[disziplin_index * 2 + 1]
                        first_pause = gruppen_disziplinen[1]
                        for disziplin in gruppen_disziplinen[2::2]:
                            self._scenario += first_pause < disziplin
                        for disziplin in gruppen_disziplinen[1::2]:
                            self._scenario += disziplin < last_disziplin
                    else:
                        for disziplin in gruppen_disziplinen[1:]:
                            self._scenario += first_disziplin < disziplin
                        for disziplin in gruppen_disziplinen[:-1]:
                            self._scenario += disziplin < last_disziplin
                    self._sequence_not_strict_gruppen.append(gruppe)

                if wettkampf_with_pausen:
                    gruppen_disziplinen_without_pausen = gruppen_disziplinen[::2]
                    for disziplin in gruppen_disziplinen_without_pausen[1:]:
                        wettkampf_disziplinen_factors[disziplin['name']] += 1
                    wettkampf_disziplinen_factors[disziplin['name']] += 1
                else:
                    gruppen_disziplinen_without_pausen = gruppen_disziplinen
                    for disziplin in gruppen_disziplinen_without_pausen[1:]:
                        wettkampf_disziplinen_factors[disziplin['name']] += 1
                    wettkampf_disziplinen_factors[disziplin['name']] += 1

            self._set_default_objective(wettkampf_disziplinen_factors, first_disziplin)
            self._last_disziplin[wettkampf_name] = last_disziplin

    _disziplinen_sequence_strict_data = ["MAN_10K", "WOM_7K", "U16M_6K"]

    def _is_wettkampf_disziplinen_sequence_strict(self, wettkampf_name):
        return wettkampf_name in self._disziplinen_sequence_strict_data

    def set_wettkampf_start_times(self, wettkampf_start_times):
        logging.debug('setting wettkampf start times...')
        for disziplinen_name, start_times in wettkampf_start_times.items():
            try:
                self._scenario += self._disziplinen[disziplinen_name] >= start_times
            except KeyError:
                pass

    def _set_default_objective(self, wettkampf_disziplinen_factors, first_disziplin):
        for disziplin_name, factor in wettkampf_disziplinen_factors.items():
            disziplin = self._disziplinen[disziplin_name]
            self._scenario += disziplin * factor
        factor_sum = sum([factor for factor in wettkampf_disziplinen_factors.values()])
        self._scenario += first_disziplin * -factor_sum

    def set_objective(self, disziplinen_factors):
        self._scenario.clear_objective()
        for disziplin_name, factor in disziplinen_factors.items():
            self._scenario += self._disziplinen[disziplin_name] * factor

    def ensure_last_wettkampf_of_the_day(self, last_wettkampf_of_the_day):
        logging.debug('ensuring last wettkampf of the day...')
        last_disziplin_of_the_day = self._last_disziplin[last_wettkampf_of_the_day]
        for wettkampf_name, last_disziplin in self._last_disziplin.items():
            if wettkampf_name != last_wettkampf_of_the_day:
                self._scenario += last_disziplin < last_disziplin_of_the_day
        
    def getGroups(self, wettkampf_name):
        return list(self._teilnehmer_data[wettkampf_name].keys())

    def getDisziplinen(self, wettkampf_name):
        return list(self._disziplinen_data[wettkampf_name])

    def solve(self, time_limit, ratio_gap=0.0, random_seed=None, threads=None, msg=1):
        logging.debug('solving problem with mip solver...')
        status = solvers.mip.solve(self._scenario, time_limit=time_limit, ratio_gap=ratio_gap, random_seed=random_seed, threads=threads, msg=msg)
        cbc_logfile_name = "cbc.log"
        if os.path.exists(cbc_logfile_name):
            with open(cbc_logfile_name) as cbc_logfile:
                logging.info(cbc_logfile.read())
        else:
            logging.info("no {!r} found".format(cbc_logfile_name))
        if not status:
            raise NoSolutionError()

        solution_as_string = str(self._scenario.solution())
        solution_filename = '{}_solution.txt'.format(self._name)
        with open(solution_filename, 'w') as f:
            f.write(solution_as_string)
        logging.info(solution_as_string)
        plotters.matplotlib.plot(self._scenario, show_task_labels=True, img_filename='{}.png'.format(self._name),
                                 fig_size=(100, 5), hide_tasks=self._hide_tasks)

    def solve_with_ortools(self, time_limit, msg=1):
        logging.debug('solving problem with ortools solver...')
        status = solvers.ortools.solve(self._scenario, time_limit=time_limit, msg=msg)
        cbc_logfile_name = "cbc.log"
        if os.path.exists(cbc_logfile_name):
            with open(cbc_logfile_name) as cbc_logfile:
                logging.info(cbc_logfile.read())
        else:
            logging.info("no {!r} found".format(cbc_logfile_name))
        if not status:
            raise NoSolutionError()

        solution_as_string = str(self._scenario.solution())
        solution_filename = '{}_solution.txt'.format(self._name)
        with open(solution_filename, 'w') as f:
            f.write(solution_as_string)
        logging.info(solution_as_string)
        plotters.matplotlib.plot(self._scenario, show_task_labels=True, img_filename='{}.png'.format(self._name),
                                 fig_size=(100, 5), hide_tasks=self._hide_tasks)
