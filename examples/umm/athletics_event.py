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
import zeitplan_xlsx_writer


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
        self._disziplinen = {}
        self._wettkampf_first_last_disziplinen = {}
        self._last_wettkampf_of_the_day = None
        self._hide_tasks = []
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

    def create_disziplinen(self, wettkampf_data, teilnehmer_data, maximum_wettkampf_duration=None, alternative_objective=False):
        self._wettkampf_data = wettkampf_data
        self._teilnehmer_data = teilnehmer_data
        self._maximum_wettkampf_duration = maximum_wettkampf_duration
        self._alternative_objective = alternative_objective
        logging.debug('creating disziplinen...')
        for wettkampf_name in wettkampf_data:
            if wettkampf_name not in teilnehmer_data:
                continue
            logging.debug("  wettkampf: {}".format(wettkampf_name))
            is_wettkampf_with_strict_sequence = wettkampf_data[wettkampf_name].get("is_wettkampf_with_strict_sequence", False)
            if wettkampf_data[wettkampf_name].get("is_last_wettkampf_of_the_day", False):
                self._last_wettkampf_of_the_day = wettkampf_name
            gruppen_names = list(teilnehmer_data[wettkampf_name].keys())
            wettkampf_disziplinen_factors = defaultdict(int)
            for gruppen_name in gruppen_names:
                logging.debug("    gruppe: {}".format(gruppen_name))
                gruppe = self._scenario.Resource(gruppen_name)
                gruppen_disziplinen = []
                for item in wettkampf_data[wettkampf_name]["disziplinen"]:
                    disziplinen_name = "{}_{}_{}".format(wettkampf_name, gruppen_name, item["name"])
                    together = item.get("together", False)
                    if together:
                        disziplinen_name = "{}_{}_to_{}_{}".format(wettkampf_name, gruppen_names[0], gruppen_names[-1], item["name"])
                    logging.debug("      disziplin: {}".format(disziplinen_name))
                    if disziplinen_name not in self._disziplinen.keys():
                        disziplinen_length = item["length"]
                        if "pause" not in disziplinen_name.lower():
                            disziplinen_length += 1
                        else:
                            disziplinen_length -= 1
                            if disziplinen_length <= 0:
                                continue
                        kwargs = {
                            "name": disziplinen_name,
                            "length": disziplinen_length,
                            "plot_color": wettkampf_data[wettkampf_name]["plot_color"],
                        }
                        disziplin = self._scenario.Task(**kwargs)
                        self._disziplinen[disziplinen_name] = disziplin
                    else:
                        disziplin = self._disziplinen[disziplinen_name]
                    gruppen_disziplinen.append(disziplin)

                    resource = item.get("resource", None)
                    if resource:
                        if not together or gruppen_name == gruppen_names[0]:
                            for resource_name in resource.split("&"):
                                disziplin += self.any_anlage(resource_name)

                    disziplin += gruppe

                    if "pause" in disziplinen_name.lower():
                        self._hide_tasks.append(disziplin)

                first_disziplin = gruppen_disziplinen[0]
                last_disziplin = gruppen_disziplinen[-1]
                wettkampf_with_pausen = "pause" in gruppen_disziplinen[1]["name"].lower()
                if is_wettkampf_with_strict_sequence:
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
                            self._scenario += gruppen_disziplinen[disziplin_index * 2] <= gruppen_disziplinen[disziplin_index * 2 + 1]
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

                gruppen_disziplinen_without_pausen = gruppen_disziplinen
                if wettkampf_with_pausen:
                    gruppen_disziplinen_without_pausen = gruppen_disziplinen[::2]
                for disziplin in gruppen_disziplinen_without_pausen[1:]:
                    wettkampf_disziplinen_factors[disziplin['name']] += 1
                wettkampf_disziplinen_factors[disziplin['name']] += 1

            self._wettkampf_first_last_disziplinen[wettkampf_name] = (first_disziplin, last_disziplin)
            if not self._alternative_objective:
                self._set_default_objective(wettkampf_disziplinen_factors, first_disziplin, last_disziplin)
            else:
                self._set_wettkampf_duration_objective(first_disziplin, last_disziplin)
                self._set_maximum_wettkampf_duration_constraint(wettkampf_name, first_disziplin, last_disziplin)
            self._last_disziplin[wettkampf_name] = last_disziplin

    def _set_default_objective(self, wettkampf_disziplinen_factors, first_disziplin, last_disziplin):
        for disziplin_name, factor in wettkampf_disziplinen_factors.items():
            disziplin = self._disziplinen[disziplin_name]
            self._scenario += disziplin * factor
        factor_sum = sum([factor for factor in wettkampf_disziplinen_factors.values()])
        self._scenario += first_disziplin * -(factor_sum - 1)

    def _set_wettkampf_duration_objective(self, first_disziplin, last_disziplin):
        self._scenario += last_disziplin - first_disziplin

    def _set_maximum_wettkampf_duration_constraint(self, wettkampf_name, first_disziplin, last_disziplin):
        self._scenario += last_disziplin <= first_disziplin + self._maximum_wettkampf_duration[wettkampf_name]

    def set_wettkampf_start_times(self, wettkampf_start_times):
        logging.debug('setting wettkampf start times...')
        for disziplinen_name, start_times in wettkampf_start_times.items():
            self._scenario += self._disziplinen[disziplinen_name] > start_times

    def set_objective(self, disziplinen_factors):
        self._scenario.clear_objective()
        for disziplin_name, factor in disziplinen_factors.items():
            self._scenario += self._disziplinen[disziplin_name] * factor

    def ensure_last_wettkampf_of_the_day(self):
        if self._last_wettkampf_of_the_day is None:
            return
        logging.debug('ensuring last wettkampf of the day...')
        last_disziplin_of_the_day = self._last_disziplin[self._last_wettkampf_of_the_day]
        for wettkampf_name, last_disziplin in self._last_disziplin.items():
            if wettkampf_name != self._last_wettkampf_of_the_day:
                self._scenario += last_disziplin < last_disziplin_of_the_day

    def getGroups(self, wettkampf_name):
        return list(self._teilnehmer_data[wettkampf_name].keys())

    def getDisziplinen(self, wettkampf_name):
        return list(self._wettkampf_data[wettkampf_name]["disziplinen"])

    def get_wettkampf_duration_summary(self):
        heading = "Wettkampf-Duration-Summary:"
        lines = []
        wettkampf_duration_sum = 0
        for wettkampf_name, (first_disziplin, last_disziplin) in self._wettkampf_first_last_disziplinen.items():
            lines.append("  {}: {}..{} ({})".format(
                wettkampf_name,
                first_disziplin.start_value,
                last_disziplin.start_value,
                last_disziplin.start_value - first_disziplin.start_value,
            ))
            wettkampf_duration_sum += last_disziplin.start_value - first_disziplin.start_value
        lines.append("cumulated-wettkampf-duration: {}".format(wettkampf_duration_sum))
        return "{}\n{}".format(heading, "\n".join(lines))

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
        with open(solution_filename, 'r') as solution_file:
            zeitplan_xlsx_writer.main(solution_file, start_time="9:00")
        logging.info(self.get_wettkampf_duration_summary())
        logging.info("objective_value: {}".format(self._scenario.objective_value()))

    def solve_with_ortools(self, time_limit, msg=1):
        logging.debug('solving problem with ortools solver...')
        status = solvers.ortools.solve(self._scenario, time_limit=time_limit, msg=msg)
        if not status:
            raise NoSolutionError()

        solution_as_string = str(self._scenario.solution())
        solution_filename = '{}_solution.txt'.format(self._name)
        with open(solution_filename, 'w') as f:
            f.write(solution_as_string)
        logging.info(solution_as_string)
        plotters.matplotlib.plot(self._scenario, show_task_labels=True, img_filename='{}.png'.format(self._name),
                                 fig_size=(100, 5), hide_tasks=self._hide_tasks)
        logging.info(self.get_wettkampf_duration_summary())
        logging.info("objective_value: {}".format(self._scenario.objective_value()))
