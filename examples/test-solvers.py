#! /usr/bin/env python
from pyschedule import Scenario, Task, Resource, solvers, plotters
import copy, collections, traceback

# planning horizon for the planning which need it
horizon = 10

# solver feedback
msg = 0

# cloud-substitute for cpoptimizer.solve, requires api_key in variable space
def solve_docloud(scenario) :
	solvers.cpoptimizer.solve_docloud(scenario,api_key=api_key,msg=msg)

solve_methods = [
solvers.pulp.solve,
solvers.pulp.solve_unit,
solvers.pulp.solve_bigm,
solvers.ortools.solve,
#solvers.cpoptimizer.solve,
solve_docloud
]

def two_task_scenario() :
	S = Scenario('Scenario_1',horizon=horizon)
	T1 = S.Task('T1')
	T2 = S.Task('T2')
	R1 = S.Resource('R1')
	R2 = S.Resource('R2')
	S += T1*2 + T2 #T1 has priority to break ties
	return S

def ZERO() :
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S.T['T1'].length = 0
	sols = ['[(T1, R1, 0, 0), (T2, R1, 0, 1)]']
	return S,sols

def NONUNIT():
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S.T['T1'].length = 5
	sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 6)]']
	return S,sols

def BOUND() : # only test lower bound, upper bound is similar
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.T['T1'] > 3
	sols = ['[(T2, R1, 0, 1), (T1, R1, 3, 4)]']
	return S,sols

def BOUNDTIGHT() : # only test tight upper bound, lower bound is similar
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.T['T1'] <= 3
	sols = ['[(T2, R1, 0, 1), (T1, R1, 2, 3)]']
	return S,sols

def LAX() :
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.T['T2'] < S.T['T1']
	sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 2)]']
	return S,sols

def LAXPLUS() :
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.T['T2'] + 1 < S.T['T1']
	sols = ['[(T2, R1, 0, 1), (T1, R1, 2, 3)]']
	return S,sols

def TIGHT() :
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.T['T2'] <= S.T['T1']
	sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 2)]']
	return S,sols

def TIGHTPLUS() :
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.T['T2'] + 1 <= S.T['T1']
	sols = ['[(T2, R1, 0, 1), (T1, R1, 2, 3)]']
	return S,sols

def COND() :
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.T['T1'] + 2 << S.T['T2']
	sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 2)]']
	return S,sols

def ALT() :
	S = two_task_scenario()
	S += S.R['R1'] | S.R['R2'] % S.T['T1']
	S += S.R['R1'] | S.R['R2'] % S.T['T2']
	sols = ['[(T1, R1, 0, 1), (T2, R2, 0, 1)]','[(T1, R2, 0, 1), (T2, R1, 0, 1)]']
	return S,sols

def MULT() :
	S = two_task_scenario()
	S += S.R['R1'] % (S.T['T1'],S.T['T2'])
	S += S.R['R2'] % (S.T['T1'],S.T['T2'])
	sols = ['[(T1, R1, 0, 1), (T1, R2, 0, 1), (T2, R1, 1, 2), (T2, R2, 1, 2)]']
	return S,sols

def ALTMULT() :
	S = two_task_scenario()
	S += S.R['R1'] | S.R['R2'] % (S.T['T1'],S.T['T2'])
	sols = ['[(T1, R1, 0, 1), (T2, R1, 1, 2)]','[(T1, R2, 0, 1), (T2, R2, 1, 2)]']
	return S,sols

def CUMUL() :
	S = two_task_scenario()
	S.R['R1'].size = 2
	S += S.R['R1'] % (S.T['T1'], S.T['T2'])
	sols = ['[(T1, R1, 0, 1), (T2, R1, 0, 1)]']
	return S,sols

def CAP():
	S = two_task_scenario()
	S += S.T['T1'] % S.R['R1']|S.R['R2']
	S += S.T['T2'] % S.R['R1']|S.R['R2']
	S += S.R['R2']['length'] <= 0
	sols = ['[(T1, R1, 0, 1), (T2, R1, 1, 2)]']
	return S,sols

def CAPSLICE():
	S = two_task_scenario()
	S += S.R['R1'] % {S.T['T1'],S.T['T2']}
	S += S.R['R1']['length'][:3] <= 1
	sols = ['[(T1, R1, 0, 1), (T2, R1, 3, 4)]']
	return S,sols



scenario_methods = [
ZERO,
NONUNIT,
BOUND,
BOUNDTIGHT,
LAX,
LAXPLUS,
TIGHT,
TIGHTPLUS,
COND,
ALT,
MULT,
ALTMULT,
CUMUL,
CAP,
CAPSLICE
]

#scenario_methods = [ZERO]


solve_method_names = collections.OrderedDict([ ('%s.%s' % (solve_method.__module__,solve_method.__name__),solve_method)
                                             for solve_method in solve_methods ])
table = [[''] + list(solve_method_names.keys()) ]

for scenario_method in scenario_methods :
	scenario_name = scenario_method.__name__
	S,sols = scenario_method()
	print(S)
	row = [scenario_name]
	for solve_method_name in solve_method_names :
		print('###############################################')
		print('%s / %s' % (solve_method_name,scenario_name))
		solve_method = solve_method_names[solve_method_name]
		S_ = copy.deepcopy(S)
		try :
			solve_method(S_)
			sol = str(S_.solution())
			valid = ( sol in sols )
			row.append(valid)
			print(sol)
		except :
			row.append('Error')
			traceback.print_exc()
	table.append(row)

# write output to file
s = ''
for row in table :
	s +=  ','.join([ str(x) for x in row ]) + '\n'
with open('solvers.csv','w') as f :
	f.write(s)
	f.close()

# plot table to screen
print('###############################################')
try :
	import pandas as pd
	df = pd.DataFrame(table[1:])
	# take last two elements in method name
	df.columns = ['scenario'] + [ '.'.join(x.split('.')[-2:]) for x in table[0][1:] ]
	df = df.set_index('scenario')
	print(df)
	with open('tmp.html','w') as f:
		f.write(df.to_html())
		f.close()
except :
	print('INFO: install pandas to get nicer table plot')
	print(s)



