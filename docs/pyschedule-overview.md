
   

# pyschedule overview

pyschedule is a package to formulate and solve resource-constrained scheduling problems, which covers a lot! Its main modelling entities are:

- **precedence relations between tasks** (e.g. this one is before this one)
- **resource requirements of tasks** (e.g. this one can be done either by him or her)

more specifically, pyschedule ...

- ... is not a general optimization language but only targets the scheduling use case. It tries to be as simple as possible but not simpler
- ... is organized in scenarios where a scenario is a list of tasks and resources
- ... exploits the python language to provide a syntax that is comparable to the usual declarative description languages
- ... scenarios can be solved using different solvers which are not part of pyschedule
- ... also offers [gantt](https://en.wikipedia.org/wiki/Gantt_chart)-chart type of plotting, since optimization without visualization does not work

### Solvers

pyschedule tries to gain the best of two worlds by supporting classical MIP-models (Mixed Integer) as well as CP solvers (Constraint Programming). All solvers interfaces are in the solvers subpackage:

- **pulp.solve(scenario,kind) :** time-indexed MIP-formulation build on top of package [pulp](https://github.com/coin-or/pulp). Use parameter "kind" to select the MIP-solver ("CBC" (default if kind is not provided), "CPLEX", "GLPK"). CBC is part of pulp and hence works out of the box.
- **pulp.solve_mon(scenario,kind) :** time-indexed MIP-formulation that is slightly better for tasks of length > 1.
- **pulp.solve_bigm(scenario,kind) :** classical bigM-type MIP-formulation build on top of package, works for small models. The specific MIP-solver can also be selected via parameter "kind".
- **ortools.solve(scenario) :** the open source CP-solver of Google, a little restricted but good to ensure feasibility of larger models. Make sure that package [ortools](https://github.com/google/or-tools) is installed.
- **cpoptimizer.solve(scenario) :** [IBM CP Optimizer](http://www-01.ibm.com/software/commerce/optimization/cplex-cp-optimizer/), requires command "oplrun" to be executable. Industrial-scale solver that runs fast on very large problems.
- **cpoptimizer.solve_docloud(scenario,api_key) :** IBM CP Optimizer hosted in the cloud, you need to provide an "api_key" which you can get [here](https://developer.ibm.com/docloud/) for a trial.
- to be continued ...

There is one pre-defined heuristic (meta-solvers):

- **listsched.solve(scenario,solve_method,task_list) :** the tasks in scenario are added according to task_list and integrated in the current plan using solve_method. If task_list is not specified, then all tasks are ordered according to the precedence constraints.


pyschedule has been tested with python 2.7 and 3.4. All solvers support a parameter "msg" to switch feedback on/off. Moreover, solvers.pulp.solve, solvers.pulp.solve_discrete and solvers.ortools.solve support a parameter "time_limit" to limit the running time.

### Constraints

#### Basic Test Cases
basic test cases that are not really constraints but still represent different capabilities:
- **ZERO :** tasks of length zero are allwed, e.g. `T1 = S.Task(length=0)`.
- **NUNUNIT :** tasks of lenght > 1 are allowed, e.g. `T1 = S.Task(length=3)`.

#### Precedences
- **BOUND :** normal bounds, e.g. `T1 > 3` or `T1 < 5`, T1 starts after time step 3 or ends before time step 5, respectively.
- **BOUNDTIGHT :** tight bounds, e.g. `T1 >= 3` or `T1 <= 5`, T1 starts at time step 3 or ends at time step 5, respectively.
- **LAX :** lax precedences, e.g. `T1 < T2`, T1 is finished before T2 starts.
- **LAXPLUS :** lax precedences with offset, e.g. `T1 + 3 < T2`, T1 is finished 3 time units before T2 starts. This can be also written as `T2 - T1 > 3`. Note that `T2 - T1 < 3` will ensure that the T2 start at most 3 time units after T1 ends.
- **TIGHT :** tight precedences, e.g. `T1 <= T2`, T2 starts exactly when T1 finishes.
- **TIGHTPLUS :** tight precedences with offset, e.g. `T1 + 3 <= T2`, T2 starts exactly 3 time units after T1 finishes. This can be also written as `T2 - T1 >= 3`. Note that `T2 - T1 <= 3` will ensure that the T2 start exactly 3 time units after T1 ends.
- **COND :** conditional precedences, e.g. `T1 + 3 << T2`, if T1 and T2 share any resource and T1 finishes before T2, then T1 is finished even 3 time units before T2 starts.


#### Resources
each task needs at least one resource. To keep the syntax concise, pyschedule used % as an operator to connect tasks and resources
- **MULT :** multiple resources, e.g. `S += T1 % [R1,R2]`, T1 uses R1 and R2.
- **ALT :** alternative resources, e.g. `S += T1 % R1|R2`, T1 uses either R1 or R2. For a list of resources L it is also possible to write `S += T1 % alt(L)` or `S += T1 % alt( R for R in L )`.
- **ALTMULT :** alternative resources which are similar for different tasks, e.g. `S += R1|R2 % [T1,T2]`, T1 and T2 either use R1 or R2, but they both use the same one.
- **CUMUL :** cumulative resources, e.g. `R1 = S.Resource('R1',size=3); S += T1 % R1*2`, R1 has size 3 and T1 uses 2 units of that size whenever run. This can be used to model worker pools or any other resource with a high multiplicity. Using a resource of size n instead n resources of size 1 often helps the solver.
- **CAP :** capacities, e.g. `R1['length'] <= 4`, the sum of the lengths of the tasks assigned to R1 must be at most 4. We can also generate other parameters, e.g. first set `T1['work'] = 3` and then `R1['work'] <= 4`.
- **CAPSLICE :** capacities, e.g. `R1['length'][:10] <= 4`, the sum of the lengths of the tasks assigned to R1 during periods 1 to 10 must be at most 4.





### Solvers vs Constraints
output of [test script](https://github.com/timnon/pyschedule/blob/master/examples/test-solvers.py):

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>pulp.solve</th>
      <th>pulp.solve_mon</th>
      <th>pulp.solve_bigm</th>
      <th>ortools.solve</th>
      <th>cpoptimizer.solve_docloud</th>
    </tr>
    <tr>
      <th>scenario</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ZERO</th>
      <td> True</td>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>NONUNIT</th>
      <td> True</td>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>BOUND</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>BOUNDTIGHT</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>LAX</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>LAXPLUS</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td> False</td>
      <td> True</td>
    </tr>
    <tr>
      <th>TIGHT</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>TIGHTPLUS</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td> False</td>
      <td> True</td>
    </tr>
    <tr>
      <th>COND</th>
      <td> True</td>
      <td> True</td>
      <td>  True</td>
      <td> False</td>
      <td> True</td>
    </tr>
    <tr>
      <th>ALT</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>MULT</th>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>ALTMULT</th>
      <td> True</td>
      <td> True</td>
      <td>  True</td>
      <td>  True</td>
      <td> True</td>
    </tr>
    <tr>
      <th>CUMUL</th>
      <td> True</td>
      <td>  True</td>
      <td> False</td>
      <td> False</td>
      <td> True</td>
    </tr>
    <tr>
      <th>CAP</th>
      <td> True</td>
      <td>  True</td>
      <td> False</td>
      <td> False</td>
      <td> True</td>
    </tr>
    <tr>
      <th>CAPSLICE</th>
      <td> True</td>
      <td>  True</td>
      <td> False</td>
      <td> False</td>
      <td> True</td>
    </tr>
  </tbody>
</table>

True means that the constraint is working, False means that the constraint has no effect, and Error means that it produces an error when using it (to be fixed).

### Solver Task Annotations

Annotations provide the solver with additional information about the scenario. An annotations are set using `T[<annotation name>] = <annotation value>`:

- **_completion_time_cost:** adds the completion time of the task times its annotaton value to the objective. This is currently the only available type of objective. Adding `S += T1*5 + T2*3` is a shortcut for setting `T1['_completion_time_cost'] = 5` and `T2['_completion_time_cost'] = 3`. This should always be supported by all solvers since it allows flow-time as well as makespan objectives.

- **_task_group:** task groups are groups of tasks that have to satisfy the same constraints. We can specify a task group by writing `T1['_task_group'] = 'a'` and `T2['_task_group'] = 'a'`, hence T1 and T2 both belong to task group `a`. This annotation speeds up the solving process if there are many tasks with the same characteristc. This is currently only supported by solvers `pulp.solve` and `pulp.solve_mon`.

### Outlook

Constraints that are only partially implemented or on the TODO list:

- **FIRST :** first/last tasks on resources, the envisioned syntax is `S += R1[3:7] < T1` to ensure that T1 is the last task on R1 in between 3 and 7
- resource-dependent precedences, the envisioned syntax is `S += R1 % T1 + 3 << T2` which ensures that only on resource R1 the conditional precedence `T1 + 3 << T2` holds. This would make conditional precedences more applicable
