




pyschedule - resource-constrained scheduling in python
======================================================

.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/gantt.png
   :alt: 

pyschedule is the easiest way to match tasks with resources. It covers
problems such as flow- and job-shop scheduling, travelling salesman,
vehicle routing with time windows, and many more combinations of theses.
Install it with pip:

.. code:: python

    pip install pyschedule

Here is a hello world example, you can also find this document as a
notebook in the examples folder. For a technical overview go to the
overview notebook.

.. code:: python

    # Load pyschedule and create a scenario with ten steps planning horizon
    from pyschedule import Scenario, solvers, plotters
    S = Scenario('hello_pyschedule',horizon=10)
    
    # Create two resources
    Alice, Bob = S.Resource('Alice'), S.Resource('Bob')
    
    # Create three tasks with lengths 1,2 and 3
    cook, wash, clean = S.Task('cook',1), S.Task('wash',2), S.Task('clean',3)
    
    # Assign tasks to resources, either Alice or Bob,
    # the %-operator connects tasks and resource
    S += cook % Alice|Bob
    S += wash % Alice|Bob
    S += clean % Alice|Bob
    
    # Solve and print solution
    S.use_makespan_objective()
    solvers.pulp.solve(S,msg=1)
    
    # Print the solution
    print(S.solution())


.. parsed-literal::

    INFO: execution time for solving mip (sec) = 0.029283761978149414
    INFO: objective = 3.0
    [(clean, Alice, 0, 3), (cook, Bob, 0, 1), (wash, Bob, 1, 3), (MakeSpan, Alice, 3, 4)]


In this example we use a makespan objective which means that we want to
minimize the completion time of the last task. Hence, Bob should do the
cooking from 0 to 1 and then do the washing from 1 to 3, whereas Alice
will only do the cleaning from 0 to 3. This will ensure that both are
done after three hours. This table representation is a little hard to
read, we can visualize the plan using matplotlib:

.. code:: python

    %matplotlib inline 
    plotters.matplotlib.plot(S,fig_size=(10,5))



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_9_0.png


pyschedule supports different solvers, classical MIP- as well as
CP-based ones. All solvers and their capabilities are listed in the
overview notebook. The default solver used above uses a standard
MIP-model in combination with CBC, which is part of package pulp. If you
have CPLEX installed (command "cplex" must be running), you can easily
switch to CPLEX using:

.. code:: python

    solvers.pulp.solve(S,kind='CPLEX')

pyschedule is under active development, there might be
non-backward-compatible changes. The base features are explained in the
following example.

Alice and Bob optimize their bike paint shop with pyschedule
============================================================

Alice and Bob are running a paint shop for bikes where they pimp bikes
with fresh colors. Today they have to paint a green and a red bike. To
get started they import pyschedule and create a new scenario. We use
hours as granularity and expect a working day of at most 10 hours, so we
set the planning horizon to 10. Some solvers do not need this parameter,
but the default solver requires it:

.. code:: python

    from pyschedule import Scenario, solvers, plotters
    S = Scenario('bike_paint_shop', horizon=10)

Then they create themselves as resources:

.. code:: python

    Alice = S.Resource('Alice')
    Bob = S.Resource('Bob')

Painting a bike takes two hours. Moreover, after the bike has been
painted, it needs to get post-processed (e.g. tires pumped) which takes
one hour (which is the default). This translates into four tasks in
total:

.. code:: python

    green_paint, red_paint = S.Task('green_paint', length=2), S.Task('red_paint', length=2)
    green_post, red_post = S.Task('green_post'), S.Task('red_post')

Clearly, one can only do the post-processing after the painting with an
arbitrary gap in between. For the red paint we are a little stricter,
here we want to start the post-processing exactly one hour after the
painting since this is the time the color takes to dry:

.. code:: python

    S += green_paint < green_post, red_paint + 1 <= red_post

Each task can be done by either Alice or Bob. Note that we use the
%-operator to assign resources to tasks:

.. code:: python

    S += green_paint % Alice|Bob
    S += green_post % Alice|Bob
    
    S += red_paint % Alice|Bob
    S += red_post % Alice|Bob

So lets have a look at the scenario:

.. code:: python

    S.clear_solution()
    print(S)


.. parsed-literal::

    ###############################################
    
    SCENARIO: bike_paint_shop / horizon: 10
    
    OBJECTIVE: 
    
    RESOURCES:
    Alice
    Bob
    
    TASKS:
    green_paint : [green_paint % Alice|Bob]
    red_paint : [red_paint % Alice|Bob]
    green_post : [green_post % Alice|Bob]
    red_post : [red_post % Alice|Bob]
    
    LAX PRECEDENCES:
    green_paint < green_post
    
    TIGHT PRECEDENCES:
    red_paint + 1 <= red_post
    
    ###############################################


We havent defined an objective yet, lets use the MakeSpan and check the
scenario again:

.. code:: python

    S.use_makespan_objective()
    print(S)


.. parsed-literal::

    ###############################################
    
    SCENARIO: bike_paint_shop / horizon: 10
    
    OBJECTIVE: MakeSpan
    
    RESOURCES:
    Alice
    Bob
    
    TASKS:
    green_paint : [green_paint % Alice|Bob]
    red_paint : [red_paint % Alice|Bob]
    green_post : [green_post % Alice|Bob]
    red_post : [red_post % Alice|Bob]
    MakeSpan : [MakeSpan % Alice]
    
    LAX PRECEDENCES:
    green_paint < green_post
    green_paint < MakeSpan
    red_paint < MakeSpan
    green_post < MakeSpan
    red_post < MakeSpan
    
    TIGHT PRECEDENCES:
    red_paint + 1 <= red_post
    
    ###############################################


Hence, we want to minimize the position of the MakeSpan task subject to
the constraint that it is scheduled after all other tasks. Thus, the
position of the MakeSpan is the length of our schedule. Now we have the
first version of our scenario, lets solve and plot it:

.. code:: python

    # Set some colors for the tasks
    task_colors = { green_paint   : '#A1D372',
                    green_post    : '#A1D372', 
                    red_paint     : '#EB4845',
                    red_post      : '#EB4845',
                    S['MakeSpan'] : '#7EA7D8'}
    
    # A small helper method to solve and plot a scenario
    def run(S) :
        if solvers.pulp.solve(S):
            %matplotlib inline
            plotters.matplotlib.plot(S,task_colors=task_colors,fig_size=(10,5))
        else:
            print('no solution exists')
    
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_29_0.png


Bob is annoyed, if he paints the red bike, he also wants to do the
post-processing, switching bikes takes too much time. We use the
following constraints to ensure this. They ensure that painting and
post-processing the red bike will both be done by either Alice or Bob.
The same holds for the green one:

.. code:: python

    # First remove the old resource to task assignments
    S -= green_paint % Alice|Bob
    S -= green_post % Alice|Bob
    S -= red_paint % Alice|Bob
    S -= red_post % Alice|Bob
    
    # Add new ones
    S += Alice|Bob % {green_paint, green_post}
    S += Alice|Bob % {red_paint, red_post}
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_31_0.png


This schedule completes after four hours and suggests to paint both
bikes at the same time. However, Alice and Bob have only a single paint
shop which they need to share:

.. code:: python

    Paint_Shop = S.Resource('Paint_Shop')
    S += red_paint % Paint_Shop
    S += green_paint % Paint_Shop
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_33_0.png


Great, everybody can still go home after five hours and have a late
lunch! Unfortunately, Alice receives a call that the red bike will only
arrive after two hours:

.. code:: python

    S += red_paint > 2
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_35_0.png


Still everybody can go home after six hours, but we encounter another
problem, it is actually quite hard to switch the paint shop from green
to red because the green color is quite sticky, this takes two hours of
external cleaning. We model this with the following conditional
precedence constraint, which says that there needs to be a break of two
hours if the red painting follows the green one:

.. code:: python

    S += green_paint + 2 << red_paint
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_37_0.png


Damn, we have a full day of seven hours, this requires a lunch between
the third and the fifth hour:

.. code:: python

    Lunch = S.Task('Lunch')
    S += Lunch > 3, Lunch < 5
    S += Lunch % {Alice, Bob}
    task_colors[Lunch] = '#7EA7D8'
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_39_0.png


Our goal so far is to minimize the MakeSpan, the final completion time
of any task. We can also make this more explicit:

.. code:: python

    # First we remove the old MakeSpan (and all corresponding constraints)
    S -= S['MakeSpan']
    
    # Then we create our own MakeSpan
    MakeSpan = S.Task('MakeSpan')
    S += MakeSpan % Alice
    S += MakeSpan > {green_post,red_post}
    S += MakeSpan*1 # add the makespan (*1) to scenario for use as objective
    task_colors[MakeSpan] = '#7EA7D8'
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_41_0.png


Alice is a morning person and wants to finish three hours of work before
lunch, that is, before the third hour:

.. code:: python

    S += Alice['length'][:3] >= 3
    run(S)



.. figure:: https://github.com/timnon/pyschedule/blob/master/pics/output_43_0.png


All this sounds quite trivial, but think about the same problem with
many bikes and many persons!
