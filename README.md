# pyschedule - fast forward resource-constrained scheduling in python

![](https://github.com/timnon/pyschedule/blob/master/pics/gantt.png)

pyschedule is the easiest way to match tasks with resources, period. It covers problems such as flow- and job-shop scheduling, travelling salesman, vehicle routing with time windows, and many more combinations of theses. Install it with pip:

```python
pip install pyschedule
```

Here is a hello world example, for a more detailed example go to the <a href="https://github.com/timnon/pyschedule/blob/master/examples/bike-shop.ipynb">bike shop notebook</a> and for a technical overview go to the <a href="https://github.com/timnon/pyschedule/blob/master/docs/pyschedule-overview.ipynb">overview notebook</a>:

```python
# load pyschedule and create a scenario with 10 steps planning horizon
import pyschedule
S = pyschedule.Scenario('hello pyschedule',horizon=10)

# create two resources
Alice, Bob = S.Resource('Alice'), S.Resource('Bob')

# create three tasks with lengths 1,2 and 3
cook, wash, clean = S.Task('cook',1), S.Task('wash',2), S.Task('clean',3)

# assign tasks to resources, either Alice or Bob,
# the %-operator connects tasks and resource
S += cook % Alice|Bob
S += wash % Alice|Bob
S += clean % Alice|Bob

# solve and print solution
S.use_makespan_objective()
pyschedule.solvers.pulp.solve(S)
print(S.solution())
```

The printout should look as follows (without the additional makespan task):

```python
[(clean, Bob, 0, 3), (wash, Alice, 0, 2), (cook, Alice, 2, 3)]
```

Here we use a makespan objective which means that we want to minimize the completion time of the last task. Hence, Alice should do the washing from 0 to 2 and then do the cooking from 2 to 3, whereas Bob will only do the cleaning from 0 to 3. This will ensure that both are done after three hours. This table representation is a little hard to read, if you want a visualization, first install matplotlib:

```python
pip install matplotlib
```

and then you can run:

```python
pyschedule.plotters.matplotlib.plot(S)
```

This should show you the following gantt chart:

![](https://github.com/timnon/pyschedule/blob/master/pics/hello-pyschedule.png)

pyschedule supports different solvers, classical MIP-based ones as well as CP. All solvers and their capabilities are listed <a href="https://github.com/timnon/pyschedule/wiki/Overview">here</a>. The default solver used above uses a standard MIP-model in combination with CBC, which is part of package <a href="https://pypi.python.org/pypi/PuLP">pulp</a>. If you have CPLEX installed (command "cplex" must be running), you can switch to CPLEX using:

```python
pyschedule.solvers.pulp.solve(S,kind='CPLEX')
```

pyschedule is under active development, there might be non-backward-compatible changes


