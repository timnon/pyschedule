import sys
sys.path.append('../src')
from pyschedule import Scenario, solvers, plotters, alt

n_teams = 10
n_stadiums = n_teams
n_slots = n_teams-1

n_plays_at_home = 4
max_n_not_at_home_periods = 3

S = Scenario('sports_scheduline',horizon=n_slots)
Stadiums = S.Resources('Stadium',num=n_stadiums)
Teams = S.Resources('T',num=n_teams)
Team2Stadium = dict(zip(Teams,Stadiums))

Games = list()
for Team0 in Teams:
	count = 1
	for Team1 in Teams:
		if Team0.name >= Team1.name:
			continue
		Game = S.Task('%s%s'%(Team0,Team1),delay_cost=2**count)
		Game[Team0.name] = 1
		Game[Team1.name] = 1
		Games.append(Game)
		Game += Team0, Team1
		Game += Team2Stadium[Team0] | Team2Stadium[Team1]
		count += 1

for Team in Team2Stadium:
	Stadium = Team2Stadium[Team]
	S += Stadium[Team.name] >= n_plays_at_home
	S += Stadium[Team.name][0:n_slots:max_n_not_at_home_periods] >= 1


if solvers.mip.solve(S,msg=0,kind='CBC'):
	import getopt
	opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
	if ('--test','') in opts:
		print('test passed')
	else:
		plotters.matplotlib.plot(S,hide_resources=Teams)
else:
	print('no solution found')
	assert(1==0)
