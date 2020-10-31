# pyschedule

pyschedule is python package to compute resource-constrained task schedules. Some features are: 

- **precedence relations:** e.g. task A should be done before task B
- **resource requirements:** e.g. task A can be done by resource X or Y
- **resource capacities:** e.g. resource X can only process a few tasks

Previous use-cases include:

- school timetables: assign teachers to classes
- beer brewing: assign equipment to brewing stages
- sport schedules: assign stadiums to games

A simple pyschedule scenario where three houshold tasks need to get assigned to two persons, Alice and Bob:

```python
from pyschedule import Scenario, solvers, plotters, alt

# the planning horizon has 10 periods
S = Scenario('household',horizon=10)

# two resources: Alice and Bob
Alice, Bob = S.Resource('Alice'), S.Resource('Bob')

# three tasks: cook, wash, and clean
cook = S.Task('cook',length=1,delay_cost=1)
wash = S.Task('wash',length=2,delay_cost=1)
clean = S.Task('clean',length=3,delay_cost=2)

# every task can be done either by Alice or Bob
cook += Alice | Bob
wash += Alice | Bob
clean += Alice | Bob

# compute and print a schedule
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.025493860244750977
INFO: objective = 1.0
[(clean, Alice, 0, 3), (cook, Bob, 0, 1), (wash, Bob, 1, 3)]
```
We can also plot the schedule as a GANTT-chart and write it to a file:

```python
plotters.matplotlib.plot(S,img_filename='pics/household.png')
```

![png](pics/household.png)

There are example notebooks <a href="https://github.com/timnon/pyschedule/tree/master/example-notebooks">here</a> and simpler examples in the <a href="https://github.com/timnon/pyschedule/tree/master/examples">examples folder</a>. Install it with pip:
```
pip install pyschedule
```



## Limits

Note that pyschedule aims to be *a general solver for small to medium-sized scheduling problems*. A typical scenario that pyschedule consists of 10 resources and 100 tasks with a planning horizon of 100 periods. If your requirements are much larger than this, then an out-of-the box solution is hard to obtain. There are some ways to speed-up pyschedule (e.g. see task groups and solver parameters). It is also possible to build heuristics on top of pyschedule to solve large-scaled scheduling problems.


## How to start

When creating a scenario using pyschedule, the following imports are recommended:

```python
from pyschedule import Scenario, solvers, plotters, alt
```

This allows the creation of a scenario:

```python
S = Scenario('hello_world',horizon=10)
```

This scenario is named `hello_world` and has a time horizon of 10 periods. The granularity of the periods depends on your problem, e.g. a period could be an hour, a week, or a day. However, having far more than 100 periods makes the computation of a schedule quite hard. Some tricks to reduce the number of periods are:

- Remove periods which are not used, like hours during the night.
- Move to a higher granularity, e.g. try a granularity of 2 hours instead of 1 hour and *round* tasks *up* if necessary.

We need at least one resource in a scenario:

```python
R = S.Resource('R')
```

It is convenient to have identical resource and variable names, like `R`. During each period, some task can be schedule this period. A resource can be anything from a person to an object like a machine in a factory. It is only required that a resource can be used by at most one task in every period.

Next we add a task to the scenario:

```python
T = S.Task('T',length=1,delay_cost=1)
```
This task has length 1, that is, it requires only 1 period to finish. Since 1 is the default length of a task, we would not have to set this explicitely. Moreover, we set the delay cost to 1, that is, delaying this job for one period increases the *cost* of a schedule by 1, which motivates to finish this task as early as possible.

We define that task `T` requires resource `R` as follows:

```python
T += R
```

Then we compute and print a schedule as follows:

```python
solvers.mip.solve(S,msg=0)
print(S.solution())
```

```
INFO: execution time for solving mip (sec) = 0.014132976531982422
INFO: objective = 0.0
[(T, R, 0, 1)]
```

The output first shows the time required to solve the problem. Also the objective is plotted. Since the cost of this schedule is only the delay cost of task `T`, which is schedule in period 0, the total cost is 0 as well. The standard way to present a schedule is a list of task-resource pairs with time requirements. E.g. the output above says that task `T` should be scheduled on resource `R` from period 0 to 1.

## Costs

It is not necessary to define cost in a scenario. In this case, a solver will simply try to find a feasible schedule. Not defining any cost will sometimes even speed up the computation. However, in most scenarios, setting at least some delay cost makes sense.


### Delay Cost

We set the delay cost of a task to 1 as follows:

```python
T = S.Task('T',delay_cost=1)
```
This means that if this task is scheduled in period 0, then there will no delay cost, if it is schedule in period 1, there will be total cost 1 and so on. Hence, it makes sense to schedule this task as early as possible. Note that delay cost can also be negative, in which case a task will be *pushed* to the end of a schedule. Also note that a task with a higher delay cost is more likely to be scheduled earlier if there are no other constraints that are preventing this. The default delay cost is `None`.


### Schedule Cost

Schedule cost can be used for optional tasks, that is, we provide some positive or negative reward if a task is scheduled:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('schedule_cost',horizon=10)
R = S.Resource('R')

# not setting a schedule cost will set it to None
T0 = S.Task('T0',length=2,delay_cost=1)
# setting the schedule cost of T1 to -1
T1 = S.Task('T1',length=2,delay_cost=1,schedule_cost=-1)

T0 += R
T1 += R
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.016648054122924805
INFO: objective = 0.0
[(T0, R, 0, 2)]
```
In the schedule above, scheduling task `T1` with schedule cost -1 would decrease the total cost by 1, but then we would have to schedule both tasks `T0` and `T1`, and hence one of them would have to start in period 2. This would result an additional delay cost of 2. Consequently, it makes more sense not to schedule `T1`.


### Resource Cost

Using a resource for some periods might imply additional resource cost:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('resource_cost',horizon=10)

# assign a cost per period of 5
R = S.Resource('R',cost_per_period=5)

T = S.Task('T',length=2,delay_cost=1)
T += R
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.01111602783203125
INFO: objective = 10.0
[(T, R, 0, 2)]
```
The total cost of the computed schedule is 5 although the single task is scheduled in the first period. This is due to the fact that scheduling any task costs 5 on resource `R`.


## Task and Resource Lists

To simplify the definition of tasks, it is possible to define task lists:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('many_tasks',horizon=10)

# create 5 tasks of the same type
T = S.Tasks('T',num=5,length=1,delay_cost=1)

print(T)
```
```
[T0, T1, T2, T3, T4]
```
We created 5 tasks of length 1 and delay cost 1. The index of the tasks is padded to the end of the given task name. Therefore, avoid task names ending with digits. Note that it would also be possible to create all tasks separately. But if they are similar, this simplifies the definition of scheduling problems. Finally, we can similarly define lists of resources:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('many_resources',horizon=10)

# create 5 resources of the same type
R = S.Resources('R',num=5)

print(R)
```
```
[R0, R1, R2, R3, R4]
```



## Resource Assignment

It is possible to assign multiple resources to a task, either we define that *one* of these resources is required or *all*:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('resources_assignment',horizon=10)

R = S.Resources('R',num=2)
T = S.Tasks('T',num=2,delay_cost=1)

# T0 requires either resource R0 or R1
T[0] += R[0] | R[1]

# T1 requires resources R0 and R1
T[1] += R[0], R[1]

# print the resources requirement
print(T[0].resources_req)
print(T[1].resources_req)
```
```
[R0|R1]
[R0, R1]
```

Note that if we have a list of resources, like above, we can also use the `alt`-operator:

```python
# T0 requires any of the resources
from pyschedule import alt
T[0] += alt(R)

# T1 requires all of the resources
T1 += R
```

Now we can solve this scenario:
```python
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.05312514305114746
INFO: objective = 1.0
[(T0, R0, 0, 1), (T1, R0, 1, 2), (T1, R1, 1, 2)]
```
Therefore, `T0` is scheduled on resource `R0` in period 0 and `T1` on resources `R0` and `R1` in period 1.


### Resource Dependencies

It is often necessary to ensure that two tasks select the same resources:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('resources_dep',horizon=10)

R = S.Resources('R',num=2)
T = S.Tasks('T',num=2,delay_cost=1)

# assign all resources to both resources
T += alt(R)

# if T[1] is assigned to any resource in R, then also T[0]
T[0] += T[1] * R
	
# plot the resource dependencies of task T0
print(T[0].tasks_req)
```
```
[T1*R0, T1*R1]
```

Now we can solve this scenario
```python
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.02900981903076172
INFO: objective = 1.0
[(T1, R0, 0, 1), (T0, R0, 1, 2)]
```
It would be better to distribute the two tasks to the two resources. However, due to the defined resource dependencies, they must be assigned to the same one.


## Restricting Periods

We can restrict the periods when a job can be scheduled or when resource is available:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('periods',horizon=10)

# restrict the periods to 2 and 3
T = S.Task('T', length=1, periods=[3,4])

# restrict the periods to the range 1..3
R = S.Resource('R', periods=range(1,4))
T += R
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.04649972915649414
INFO: objective = 0.0
[(T, R, 3, 4)]
```
Clearly, due to the periods restrictions, the only possible period to schedule task `T` is 3.


## Bounds

Another way to restrict the periods when a task can be scheduled are bounds:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('bounds',horizon=10)
T = S.Task('T', length=1, delay_cost=1)
R = S.Resource('R')
T += R

# add the constraints that T needs to get schedule after period 1 but before 5
S += T > 1, T < 5

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.03368401527404785
INFO: objective = 1.0
[(T, R, 1, 2)]
```

This contraint is a *lax* bound, that is, task `T` can be schedule in any point after period 1. If we want to enforce when exactly `T` is scheduled, we can use a *tight* bound. E.g. to force `T` to be schedule exactly after period 1, we can write:

```python
S += T >= 1
```


## Precedences

Tasks often need to get scheduled in a certain order:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('lax_precedence',horizon=10)
R = S.Resource('R')
T = S.Tasks('T',num=2,length=1,delay_cost=1)
T += R

# give T0 a higher delay cost
T[0].delay_cost = 2
# add a precedence constraint to ensure that it is still scheduled one period after T1 finishes
S += T[1] + 1 < T[0] 

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.019501924514770508
INFO: objective = 4.0
[(T1, R, 0, 1), (T0, R, 2, 3)]
```

Since task `T0` is delayed two periods, we get a total delay cost of 4. If we would not have the precedence constraint, we could schedule `T0` first and only get delay cost 1. Note that the `+ 1` is optional.

We call this a *lax* precedence constraint. Similarly to tight bounds, *tight* precedence constraints additionally ensure that jobs are executed directly after each other:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('tight_precedence',horizon=10)
R = S.Resource('R')
T = S.Tasks('T',num=2,length=1,delay_cost=2)
T += R

# give T0 a negative delay cost
T[0].delay_cost = -1 
# ensure that T[0] is scheduled exactly two periods after T[1]
S += T[1] + 2 <= T[0] 

solvers.mip.solve(S,msg=1)
print(S.solution())
```

```
INFO: execution time for solving mip (sec) = 0.016117095947265625
INFO: objective = -3.0
[(T1, R, 0, 1), (T0, R, 3, 4)]
```

Since `T0` has negative delay cost, it would be pushed to the end of the schedule, but the tight precedence constraint ensures that it is scheduled two periods after `T1` finishes. If the delay cost of `T1` would be smaller than `T0`, than both tasks would be pushed to the end of the schedule. 


### Conditional Precedences

It is often required that precedence constraints are only applied if two tasks are assigned to the same resource, e.g. if we want to ensure that a certain task is the last one that runs on some resource:

```python
from pyschedule import Scenario, solvers, plotters, alt
S = Scenario('cond_precedence',horizon=10)
R = S.Resources('R',num=2)

T = S.Task('T',length=1,delay_cost=1)
T_final = S.Tasks('T_final',num=2,length=1,delay_cost=1)
T_final[0] += R[0]
T_final[1] += R[1]
T += alt(R)

# conditional precedences
S += T * R[0] < T_final[0]
S += T * R[1] < T_final[1]

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.040048837661743164
INFO: objective = 1.0
[(T, R0, 0, 1), (T_final1, R1, 0, 1), (T_final0, R0, 1, 2)]
```
The first conditional precedence implies that if task `T` is scheduled on `R[0]`, then `T_final[0]` is scheduled afterwards. Therefore, it is allowed that `T_final[1]` is scheduled in the same period as `T` since `T` is not scheduled on `R[1]`.


## Capacities

Capacity constraints can be used to restrict the number tasks which are executed during a certain time period:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('capacities',horizon=10)
R = S.Resource('R')
T = S.Tasks('T',num=4,length=1,delay_cost=1)
T += R

# capacity constraint to limit the number of tasks until period 5 to 3
S += R[0:5] <= 3

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.015291213989257812
INFO: objective = 8.0
[(T3, R, 0, 1), (T0, R, 1, 2), (T1, R, 2, 3), (T2, R, 5, 6)]
```

Due to the capacity constraint, one task is scheduled after period 5. If not defined otherwise, the capacity constraint is applied to the lengths of the task. That is, the sum of lengths of tasks before period 5 is required to be at most 3. We can make this more explicit by writing:

```python
S += R['length'][0:5] <= 3
```

Finally, if we want to bound the maximum instead of the sum, we can write:
```python
S += R['length'][0:5].max <= 3
```

### Non-unit Tasks

Cases where task lengths are larger than one deserve a special treatment:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('capacities',horizon=10)
R = S.Resource('R')

# task with non-unit length
T = S.Task('T',length=4,delay_cost=1)
T += R

S += R[0:5] <= 3

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.022754907608032227
INFO: objective = 2.0
[(T, R, 2, 6)]
```
Task `T` has to start in period 2 because of the capacity constraint. This is possible because the length of the part of this task which lies within the capacity constraint is 3. Specifically, the part scheduled in periods 2,3 and 4. This holds in general, a task contributes to a standard capacity constraint proportionally to how much it *overlaps* with the capacity constraint. This generalizes to user-defined task attributes as described in the next section.

### User-Defined Task Attributes

We can apply capacity constraints to all task attributes, not just the task lengths, but also user-defined ones:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('capacities_myattribute',horizon=10)
R = S.Resource('R')

# define the additional property named myproperty uniformly as 1
T = S.Tasks('T',num=4,length=1,delay_cost=1,myattribute=1)
# set it to 0 for the first task
T[0].myattribute = 0
T += R

# the sum of myproperty must be smaller than 3 until period 5
S += R['myattribute'][0:5] <= 3

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.018787145614624023
INFO: objective = 6.0
[(T3, R, 0, 1), (T0, R, 1, 2), (T1, R, 2, 3), (T2, R, 3, 4)]
```
Since `T[0]` does not add anything to the sum of the myattribute-values before period 5, all tasks can be scheduled before this period.


### Bounding Differences

The default way to aggregate within the range of a capacity constraint is to summarize. On the other hand, if we want to ensure that some attribute does not change too much over time, we can also restrict the sum of differences of this attribute:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('capacities_diff',horizon=10)
R = S.Resource('R')

T = S.Tasks('T',num=4,length=1,delay_cost=1,myattribute=1)
T[0].delay_cost = 2
T[0].myattribute = 0
T[1].delay_cost = 2
T[1].myattribute = 0
T += R
 
# limit the sum of differences of myattribute to 1
S += R['myattribute'].diff <= 1

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.05473184585571289
INFO: objective = 11.0
[(T3, R, 0, 1), (T2, R, 1, 2), (T0, R, 2, 3), (T1, R, 3, 4)]
```
Note that if we do not define the range of a capacity constraint like above, then the constraint is applied to the complete time horizon. In the scenario above, it would be advantageous to schedule tasks `T[0]` and `T[1]` as early as possible, since they have a higher delay cost. However, if would schedule them in periods 0 and 1, respectively, and directly afterwards `T[2]` and `T[3]`, then myattribute would first increase by 1 in period 2 and afterwards decrease again by 1 in period 4, resulting in a sum of differences of 2.

The `.diff`-capacity constraint limits the sum of increases and decreases. If we only want to limit the increases or decreases, then we can use `.diff_up` or `.diff_down`, respectively.


### Combining Constraints

We can combine capacity constraints doing natural arithmetic:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('capacities_arithmetic',horizon=10)
R = S.Resource('R')

T = S.Tasks('T',num=4,length=1,delay_cost=1,myattribute=1)
T += R
 
# add two capacities
S += R['myattribute'][:3] + R['myattribute'][5:7] <= 1

solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.03471493721008301
INFO: objective = 14.0
[(T3, R, 0, 1), (T2, R, 3, 4), (T1, R, 4, 5), (T0, R, 7, 8)]
```
Since one task is schedule in period 0, we cannot schedule any more tasks in periods 0 to 2 or in periods 5 to 6 . Therefore, we squeeze in two tasks in periods 3 and 4 and one task in period 7.


## Task Groups

There are often task redundancies in a planning project, e.g. there might be a group of tasks which are interchangeable. That is, they could be swapped in the schedule without changing its cost or feasibility. Given this information in the `is_group`-attribute, this can be exploited by the solver to often drastically speed-up the computation:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('task_groups',horizon=10)
R = S.Resource('R')

# these tasks are interchangeable
T = S.Tasks('T',num=10,length=1,delay_cost=1,is_group=True)
T += R
 
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.01534271240234375
INFO: objective = 45.0
[(T0, R, 0, 1), (T1, R, 1, 2), (T2, R, 2, 3), (T3, R, 3, 4), (T4, R, 4, 5), (T5, R, 5, 6), (T6, R, 6, 7), (T7, R, 7, 8), (T8, R, 8, 9), (T9, R, 9, 10)]
```
Running this with setting `is_group=False` only slightly increases the running time, but there are scenarios where this difference is much more significant:
```
INFO: execution time for solving mip (sec) = 0.025635719299316406
INFO: objective = 45.0
[(T7, R, 0, 1), (T0, R, 1, 2), (T4, R, 2, 3), (T2, R, 3, 4), (T5, R, 4, 5), (T6, R, 5, 6), (T1, R, 6, 7), (T9, R, 7, 8), (T8, R, 8, 9), (T3, R, 9, 10)]
```

**CAUTION**: combining task groups with capacities with resource dependencies might not work in some cases.


<!---

## Resource Sizes

Consider the case that we have a pool of workers which are interchangeable. To improve the performance of the solver, we can implement this with *larger* resources which can schedule tasks in parallel:

```python
from pyschedule import Scenario, solvers, plotters
S = Scenario('capacities_arithmetic',horizon=10)

# this resource can schedule three tasks in parallel
R = S.Resource('R',size=2)

T = S.Tasks('T',num=4,length=1,delay_cost=1)
T += R
 
solvers.mip.solve(S,msg=1)
print(S.solution())
```
```
INFO: execution time for solving mip (sec) = 0.016080141067504883
INFO: objective = 2.0
[(T2, R, 0, 1), (T3, R, 0, 1), (T0, R, 1, 2), (T1, R, 1, 2)]
```
We see that the always two tasks are scheduled in parallel on the single resource.
-->

## Solver Parameters

The default pyschedule backend is a <a href="https://en.wikipedia.org/wiki/Integer_programming">time-indexed mixed integer formulation (MIP)</a>. There are the following parameters:

- **msg**: show info on/off (default is 0)
- **time_limit**: limit the solving time in seconds (default is None)
- **ratio_gap**: stop the solving process when this integrality gap is reached, e.g. 1.2 stands for 20% gap to optimality (default is None)
- **random_seed**: the random seed used by the solver (default is 42)
- **kind**: the Integer Programming backend to use. The default is `CBC` which comes preinstalled with package `pulp`. If <a href="http://scip.zib.de/">SCIP</a> is installed (command `scip` must be running), you can use `SCIP`. Finally, if you have <a href="https://www.ibm.com/analytics/data-science/prescriptive-analytics/cplex-optimizer">CPLEX</a> installed (command `cplex` must be running), you can use `CPLEX`

E.g. this could be used as follows:

```python
solvers.mip.solve(S,kind='CPLEX',time_limit=60,random_seed=42,msg=1)
```

## Plotter Parameters

The default pyschedule backend to plot a schedule is <a href="https://matplotlib.org/">matplotlib</a>. Some parameters are:

- **img_filename**: write the plot as a `.png`-file (default is None)
- **fig_size**: size of the plot (default is (15,5))
- **resource_height**: the height of a resource in the plot (default is 1)
- **show_task_labels**: show the labels of tasks in the plot (default is True)
- **hide_tasks**: list of tasks not to plot (default is [])
- **hide_resources**: list of resources to hide in the plot (default is [])
- **task_colors**: a mapping of tasks to colors (default is empty dictionary)
- **vertical_text**: write the task labels vertically (default if False)

E.g. this could be used as follows:

```python
plotters.matplotlib.plot(S,img_filename='tmp.png',fig_size=(5,5),hide_tasks=[T])
```


**FINAL CAUTION:** pyschedule is under active development, there might be non-backward-compatible changes.

 
 
## Appendix

```python
import sys
sys.path.append('src')
``` 
