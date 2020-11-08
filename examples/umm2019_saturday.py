# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path.append('../src')
import getopt
opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
from pyschedule import Scenario, solvers, plotters, alt

scenario = Scenario('umm_saturday', horizon=144)

Laeufe = scenario.Resource('Läufe')
Weit = scenario.Resource('Weit', size=2)
Kugel = scenario.Resource('Kugel', size=2)
Hoch = scenario.Resource('Hoch', size=2)
Diskus = scenario.Resource('Diskus')

Gr24 = scenario.Resource('Gr24')
Gr25 = scenario.Resource('Gr25')
Gr30 = scenario.Resource('Gr30')
Gr31 = scenario.Resource('Gr31')
Gr32 = scenario.Resource('Gr32')
Gr33 = scenario.Resource('Gr33')
Gr34 = scenario.Resource('Gr34')

U16M_Gr24_100mHue = scenario.Task('U16M_Gr24_100mHü', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr24_Weit = scenario.Task('U16M_Gr24_Weit', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr24_Kugel = scenario.Task('U16M_Gr24_Kugel', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr24_Hoch = scenario.Task('U16M_Gr24_Hoch', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr24_Diskus = scenario.Task('U16M_Gr24_Diskus', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr24_to_Gr25_1000m = scenario.Task('U16M_Gr24_to_Gr25_1000m', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr25_100mHue = scenario.Task('U16M_Gr25_100mHü', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr25_Weit = scenario.Task('U16M_Gr25_Weit', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr25_Kugel = scenario.Task('U16M_Gr25_Kugel', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr25_Hoch = scenario.Task('U16M_Gr25_Hoch', length=2, delay_cost=1, plot_color='lightblue')
U16M_Gr25_Diskus = scenario.Task('U16M_Gr25_Diskus', length=2, delay_cost=1, plot_color='lightblue')

U16M_Gr24_100mHue += Laeufe, Gr24
U16M_Gr25_100mHue += Laeufe, Gr25
U16M_Gr24_Weit += Weit, Gr24
U16M_Gr25_Weit += Weit, Gr25
U16M_Gr24_Kugel += Kugel, Gr24
U16M_Gr25_Kugel += Kugel, Gr25
U16M_Gr24_Hoch += Hoch, Gr24
U16M_Gr25_Hoch += Hoch, Gr25
U16M_Gr24_Diskus += Diskus, Gr24
U16M_Gr25_Diskus += Diskus, Gr25
U16M_Gr24_to_Gr25_1000m += Laeufe, Gr24

scenario += U16M_Gr24_100mHue+2 < U16M_Gr24_Weit
scenario += U16M_Gr24_Weit+2 < U16M_Gr24_Kugel
scenario += U16M_Gr24_Kugel+2 < U16M_Gr24_Hoch
scenario += U16M_Gr24_Hoch+2 < U16M_Gr24_Diskus
scenario += U16M_Gr24_Diskus+2 < U16M_Gr24_to_Gr25_1000m

scenario += U16M_Gr25_100mHue+2 < U16M_Gr25_Weit
scenario += U16M_Gr25_Weit+2 < U16M_Gr25_Kugel
scenario += U16M_Gr25_Kugel+2 < U16M_Gr25_Hoch
scenario += U16M_Gr25_Hoch+2 < U16M_Gr25_Diskus
scenario += U16M_Gr25_Diskus+2 < U16M_Gr24_to_Gr25_1000m

U12M_Gr30_60m = scenario.Task('U12M_Gr30_60m', length=2, delay_cost=1, plot_color='yellow')
U12M_Gr30_Weit = scenario.Task('U12M_Gr30_Weit', length=6, delay_cost=1, plot_color='yellow')
U12M_Gr30_Kugel = scenario.Task('U12M_Gr30_Kugel', length=4, delay_cost=1, plot_color='yellow')
U12M_Gr30_to_Gr34_600m = scenario.Task('U12M_Gr30_to_Gr34_600m', length=2, delay_cost=1, plot_color='yellow')
U12M_Gr31_60m = scenario.Task('U12M_Gr31_60m', length=2, delay_cost=1, plot_color='yellow')
U12M_Gr31_Weit = scenario.Task('U12M_Gr31_Weit', length=6, delay_cost=1, plot_color='yellow')
U12M_Gr31_Kugel = scenario.Task('U12M_Gr31_Kugel', length=4, delay_cost=1, plot_color='yellow')
U12M_Gr32_60m = scenario.Task('U12M_Gr32_60m', length=2, delay_cost=1, plot_color='yellow')
U12M_Gr32_Weit = scenario.Task('U12M_Gr32_Weit', length=6, delay_cost=1, plot_color='yellow')
U12M_Gr32_Kugel = scenario.Task('U12M_Gr32_Kugel', length=4, delay_cost=1, plot_color='yellow')
U12M_Gr33_60m = scenario.Task('U12M_Gr33_60m', length=2, delay_cost=1, plot_color='yellow')
U12M_Gr33_Weit = scenario.Task('U12M_Gr33_Weit', length=6, delay_cost=1, plot_color='yellow')
U12M_Gr33_Kugel = scenario.Task('U12M_Gr33_Kugel', length=4, delay_cost=1, plot_color='yellow')
U12M_Gr34_60m = scenario.Task('U12M_Gr34_60m', length=2, delay_cost=1, plot_color='yellow')
U12M_Gr34_Weit = scenario.Task('U12M_Gr34_Weit', length=6, delay_cost=1, plot_color='yellow')
U12M_Gr34_Kugel = scenario.Task('U12M_Gr34_Kugel', length=4, delay_cost=1, plot_color='yellow')

U12M_Gr30_60m += Laeufe, Gr30
U12M_Gr31_60m += Laeufe, Gr31
U12M_Gr32_60m += Laeufe, Gr32
U12M_Gr33_60m += Laeufe, Gr33
U12M_Gr34_60m += Laeufe, Gr34

U12M_Gr30_Weit += Weit, Gr30
U12M_Gr31_Weit += Weit, Gr31
U12M_Gr32_Weit += Weit, Gr32
U12M_Gr33_Weit += Weit, Gr33
U12M_Gr34_Weit += Weit, Gr34

U12M_Gr30_Kugel += Kugel, Gr30
U12M_Gr31_Kugel += Kugel, Gr31
U12M_Gr32_Kugel += Kugel, Gr32
U12M_Gr33_Kugel += Kugel, Gr33
U12M_Gr34_Kugel += Kugel, Gr34

U12M_Gr30_to_Gr34_600m +=  Laeufe, Gr30

scenario += U12M_Gr30_60m < U12M_Gr31_60m
scenario += U12M_Gr31_60m < U12M_Gr32_60m
scenario += U12M_Gr32_60m < U12M_Gr33_60m
scenario += U12M_Gr33_60m < U12M_Gr34_60m

scenario += U12M_Gr30_60m+2 < U12M_Gr30_Weit
scenario += U12M_Gr30_60m+2 < U12M_Gr30_Kugel
scenario += U12M_Gr30_60m+2 < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr30_60m+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr30_Weit+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr30_Kugel+2

scenario += U12M_Gr31_60m+2 < U12M_Gr31_Weit
scenario += U12M_Gr31_60m+2 < U12M_Gr31_Kugel
scenario += U12M_Gr31_60m+2 < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr31_60m+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr31_Weit+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr31_Kugel+2

scenario += U12M_Gr32_60m+2 < U12M_Gr32_Weit
scenario += U12M_Gr32_60m+2 < U12M_Gr32_Kugel
scenario += U12M_Gr32_60m+2 < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr32_60m+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr32_Weit+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr32_Kugel+2

scenario += U12M_Gr33_60m+2 < U12M_Gr33_Weit
scenario += U12M_Gr33_60m+2 < U12M_Gr33_Kugel
scenario += U12M_Gr33_60m+2 < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr33_60m+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr33_Weit+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr33_Kugel+2

scenario += U12M_Gr34_60m+2 < U12M_Gr34_Weit
scenario += U12M_Gr34_60m+2 < U12M_Gr34_Kugel
scenario += U12M_Gr34_60m+2 < U12M_Gr30_to_Gr34_600m

scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr34_60m+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr34_Weit+2
scenario += U12M_Gr30_to_Gr34_600m > U12M_Gr34_Kugel+2


print("scenario: {}".format(scenario))

if solvers.mip.solve(scenario, time_limit=600, msg=1):
    print(scenario.solution())
    plotters.matplotlib.plot(scenario, show_task_labels=True)
else:
    print('no solution found')
    assert(1==0)
