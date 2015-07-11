#! /usr/bin/env python
import pyschedule
import copy, collections, traceback


horizon = 10

solve_methods = [
pyschedule.solvers.pulp.solve,
pyschedule.solvers.pulp.solve_discrete,
pyschedule.solvers.ortools.solve,
pyschedule.solvers.cpoptimizer.solve
]

def two_task_scenario() :
	S = pyschedule.Scenario('Scenario_1')
	T1 = S.Task('T1')
	T2 = S.Task('T2')
	R1 = S.Resource('R1')
	R2 = S.Resource('R2')
	S += T1*2 + T2
	return S

def zero_task() :
	S = two_task_scenario()
	S.R['R1'] += S.T['T1'],S.T['T2']
	S.T['T1'].length = 0
	sols = ['[(T1, R1, 0, 0), (T2, R1, 0, 1)]']
	return S,sols

def bound_low() :
	S = two_task_scenario()
	S.R['R1'] += S.T['T1'],S.T['T2']
	S += S.T['T1'] > 3
	sols = ['[(T2, R1, 0, 1), (T1, R1, 3, 4)]']
	return S,sols

def precedence() :
	S = two_task_scenario()
	S.R['R1'] += S.T['T1'],S.T['T2']
	S += S.T['T1'] < S.T['T2']
	sols = ['[(T1, R1, 0, 1), (T2, R1, 1, 2)]']
	return S,sols

def precedence_offset() :
	S = two_task_scenario()
	S.R['R1'] += S.T['T1'],S.T['T2']
	S += S.T['T1'] + 1 < S.T['T2']
	sols = ['[(T1, R1, 0, 1), (T2, R1, 2, 3)]']
	return S,sols

def precedence_tight() :
	S = two_task_scenario()
	S.R['R1'] += S.T['T1'],S.T['T2']
	S += S.T['T1'] <= S.T['T2']
	sols = ['[(T1, R1, 0, 1), (T2, R1, 1, 2)]']
	return S,sols

def precedence_tight_offset() :
	S = two_task_scenario()
	S.R['R1'] += S.T['T1'],S.T['T2']
	S += S.T['T1'] + 1 <= S.T['T2']
	sols = ['[(T1, R1, 0, 1), (T2, R1, 2, 3)]']
	return S,sols

def precedence_cond() :
	S = two_task_scenario()
	S.R['R1'] += S.T['T1'],S.T['T2']
	S += S.T['T1'] + 2 << S.T['T2']
	sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 2)]']
	return S,sols

def alt_resources() :
	S = two_task_scenario()
	S.T['T1'] += S.R['R1'] | S.R['R2']
	S.T['T2'] += S.R['R1'] | S.R['R2']
	sols = ['[(T1, R1, 0, 1), (T2, R2, 0, 1)]','[(T1, R2, 0, 1), (T2, R1, 0, 1)]']
	return S,sols

def alt_resources_two() :
	S = two_task_scenario()
	S.T['T1'] += S.R['R1'], S.R['R2']
	S.T['T2'] += S.R['R1'], S.R['R2']
	sols = ['[(T1, R1, 0, 1), (T1, R2, 0, 1), (T2, R1, 1, 2), (T2, R2, 1, 2)]']
	return S,sols

def cumul_resource() :
	S = two_task_scenario()
	S.R['R1'].size = 2
	S.R['R1'] += S.T['T1'], S.T['T2']
	sols = ['[(T1, R1, 0, 1), (T2, R1, 0, 1)]']
	return S,sols
	

scenario_methods = [
zero_task,
bound_low,
precedence,
precedence_offset,
precedence_tight,
precedence_tight_offset,
precedence_cond,
alt_resources,
alt_resources_two,
cumul_resource
]



solve_method_names = collections.OrderedDict([ ('%s.%s' % (solve_method.__module__,solve_method.__name__),solve_method)
                                             for solve_method in solve_methods ])
table = [[''] + list(solve_method_names.keys()) ]

for scenario_method in scenario_methods :
	scenario_name = scenario_method.__name__
	S,sols = scenario_method()
	row = [scenario_name]
	for solve_method_name in solve_method_names :
		solve_method = solve_method_names[solve_method_name]
		S_ = copy.deepcopy(S)
		try :
			if 'horizon' in solve_method.__code__.co_varnames :
				solve_method(S_,horizon=horizon)
			else :
				solve_method(S_)
			sol = str(S_.solution())
			valid = ( sol in sols )
			row.append(valid)
			print('###############################################')
			print('%s / %s' % (solve_method_name,scenario_name))
			print(sol)
		except :
			row.append('na')
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
except :
	print('INFO: install pandas to get nicer table plot')
	print(s)




