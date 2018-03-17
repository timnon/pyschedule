


# pyschedule overview

pyschedule is a package to formulate and solve resource-constrained scheduling problems, which covers a lot! Its main modelling entities are:

- **precedence relations between tasks** (e.g. this one is before this one)
- **resource requirements of tasks** (e.g. this one can be done either by her or him)
- **capacities** (e.g. he can only do that many)

more specifically, pyschedule ...

- ... is not a general optimization language but only targets the scheduling use case. It tries to be as simple as possible but not simpler
- ... is organized in scenarios where a scenario is a list of tasks and resources
- ... exploits the python language to provide a syntax that is comparable to the usual declarative description languages
- ... scenarios can be solved using different solvers which are not part of pyschedule
- ... also offers [gantt](https://en.wikipedia.org/wiki/Gantt_chart)-chart type of plotting, since optimization without visualization does not work

### Solvers

pyschedule tries to gain the best of two worlds by supporting classical MIP-models (Mixed Integer) as well as CP solvers (Constraint Programming). All solvers interfaces are in the solvers subpackage:

- **mip.solve(scenario,kind) :** time-indexed MIP-formulation build on top of package [pulp](https://github.com/coin-or/pulp). Use parameter "kind" to select the MIP-solver ("CBC" (default if kind is not provided), "CPLEX", "GLPK", "SCIP"). CBC is part of pulp and hence works out of the box. For CBC, CPLEX and SCIP, you can pass parameters "time_limit" or "ratio_gap" (only CBC and SCIP) to limit the running time and receive suboptimal solutions.
- **mip.solve_bigm(scenario,kind) :** classical bigM-type MIP-formulation, works for small models.

There are some more solvers not based on MIPs, but they are not supported that well yet:

- **ortools.solve(scenario) :** the open source CP-solver of Google, a little restricted but good to ensure feasibility of larger models. Make sure that package [ortools](https://github.com/google/or-tools) is installed.
- **cpoptimizer.solve(scenario) :** [IBM CP Optimizer](http://www-01.ibm.com/software/commerce/optimization/cplex-cp-optimizer/), requires command "oplrun" to be executable. Industrial-scale solver that runs fast on very large problems.
- **cpoptimizer.solve_docloud(scenario,api_key) :** IBM CP Optimizer hosted in the cloud, you need to provide an "api_key" which you can get [here](https://developer.ibm.com/docloud/) for a trial.
- to be continued ...

There is one pre-defined heuristic (meta-solver):

- **listsched.solve(scenario,solve_method,task_list,batch_size) :** all tasks are added in the order of task_list and integrated in the current schedule using solve_method. If task_list is not specified, then an ordering according to the precedence constraints is used as default.


pyschedule has been tested with python 2.7 and 3.4. All solvers support a parameter "msg" to switch feedback on/off. Moreover, solvers.pulp.solve, solvers.pulp.solve_discrete and solvers.ortools.solve support a parameter "time_limit" to limit the running time.

### Constraints

#### Basic Test Cases
basic test cases that are not really constraints but still represent different capabilities:
- **ZERO :** tasks of length zero are allwed, e.g. `T1 = S.Task(length=0)`.
- **NONUNIT :** tasks of lenght > 1 are allowed, e.g. `T1 = S.Task(length=3)`.

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
- **MULT :** multiple resources, e.g. `T1 += [R1,R2]`, T1 uses R1 and R2.
- **ALT :** alternative resources, e.g. `T1 += R1|R2`, T1 uses either R1 or R2. For a list of resources L it is also possible to write `T1 += pyschedule.alt(L)` or `T1 += pyschedule.alt( R for R in L )`.
- **ALTMULT :** alternative resources which are similar for different tasks, e.g. `A = R1|R2; T1 += A; T2 += A`, T1 and T2 either use R1 or R2, but they both use the same one.
- **CUMUL :** cumulative resources, e.g. `R1 = S.Resource('R1',size=3); T1 += R1*2`, R1 has size 3 and T1 uses 2 units of that size whenever run. This can be used to model worker pools or any other resource with a high multiplicity. Using a resource of size n instead n resources of size 1 often helps the solver.
- **CAP :** capacities, e.g. `R1['length'] <= 4`, the sum of the lengths of the tasks assigned to R1 must be at most 4. We can also generate other parameters, e.g. first set `T1.work = 3` and then `R1['work'] <= 4`.
- **CAPSLICE :** capacities, e.g. `R1['length'][:10] <= 4`, the sum of the lengths of the tasks assigned to R1 during periods 0 to 9 must be at most 4. In case a task starts before period 9 and ends after period 9, the capacity requirement of this task is proportional to the overlap
- **CAPDIFF :** change in capacity over time like a derivate, e.g. `R1['length'].diff <= 4`, the number of times resource R switches from running to not running or vice versa is at most 4. We can also use other parameters than length, e.g. first set `T1.work = 3` and then `R1['work'].diff <= 4`.
- **CAPDIFFSLICE :** change of capacity over time in slice, e.g. `R1['length'][:10].diff <= 4`, the number of times resource R switches from running to not running or vice versa in periods 0 to 9 is at most 4
- **REQUIRED :** make a task optional, e.g. `T1.required = False`


### Solvers vs Constraints
output of [test script](https://github.com/timnon/pyschedule/blob/master/examples/test-solvers.py):

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mip.solve</th>
      <th>mip.solve_bigm</th>
      <th>ortools.solve</th>
    </tr>
    <tr>
      <th>scenario</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ZERO</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>NONUNIT</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>BOUND</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>BOUNDTIGHT</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>LAX</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>LAXPLUS</th>
      <td>X</td>
      <td>X</td>
      <td></td>
    </tr>
    <tr>
      <th>TIGHT</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>TIGHTPLUS</th>
      <td>X</td>
      <td>X</td>
      <td></td>
    </tr>
    <tr>
      <th>COND</th>
      <td>X</td>
      <td>X</td>
      <td></td>
    </tr>
    <tr>
      <th>ALT</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>MULT</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>ALTMULT</th>
      <td>X</td>
      <td>X</td>
      <td>X</td>
    </tr>
    <tr>
      <th>CUMUL</th>
      <td>X</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>CAP</th>
      <td>X</td>
      <td>X</td>
      <td></td>
    </tr>
    <tr>
      <th>CAPSLICE</th>
      <td>X</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>CAPDIFF</th>
      <td>X</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>CAPDIFFSLICE</th>
      <td>X</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>REQUIRED</th>
      <td>X</td>
      <td></td>
      <td></td>
    </tr>
  </tbody>
</table>

X means that the constraint is working and Error means that it produces an error when using it (to be fixed).

### Outlook

Constraints that are only partially implemented or on the TODO list:

- price-collecting objective: reward for every scheduled job, but some jobs can be omitted
- **FIRST :** first/last tasks on resources, the envisioned syntax is `S += R1[3:7] < T1` to ensure that T1 is the last task on R1 in between 3 and 7
- soft constraints with cost for not satisfying, the envisoned syntax is `S += soft( T < 5, cost=3 )`
- turn solvers.pulp into solvers.mip which is agnostic of the python mip package
