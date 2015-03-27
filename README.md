# pyschedule - fast forward resource-constrained scheduling in python

![](https://github.com/timnon/pyschedule/blob/master/pics/gantt.png)

pyschedule is the easiest way to match tasks with resources, period. It covers problems such as ffow- and job-shop scheduling, travelling salesman, vehicle routing with time windows, and many more combinations of theses. Install it with pip:

```
pip install pyschedule
```

This is how it works:

```
# load pyschedule and create a scenario
from pyschedule import *
S = pyschedule.Scenario('hello pyschedule')

# create two resources
Alice, Bob = S.Resource('Alice'), S.Resource('Bob')

# create three tasks with lengths 1,2 and 3
cook, wash, clean = S.Task('cook',1), S.Task('wash',2), S.Task('clean',3)

# assign tasks to resources, either Alice or Bob
cook += Alice | Bob
wash += Alice | Bob
clean += Alice | Bob

# solve and print solution
solvers.pulp().solve(S)
print S.solution()
```

The printout should look as follows:

```
[('wash', 'Alice', 0.0, 2.0), ('cook', 'Alice', 2.0, 3.0), ('clean', 'Bob', 0.0, 3.0)]
```

The default objective is to minimize the latest completion time of any task (MakeSpan). Hence, Alice should do the washing from 0 to 2 and then do the cooking from 2 to 3, whereas Bob will only do the cleaning from 0 to 3. This will ensure that both are done after three hours. This table representation is a little hard to read, if you want a visualization, first install matplotlib:

```
pip install matplotlib
```

and then you can run:

```
plotters.gantt_matplotlib().plot(S)
```

This should plot a nice gantt chart in a pop-up.

