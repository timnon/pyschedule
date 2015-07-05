#! /usr/bin/env python
import pyschedule
import copy, collections


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
	


scenario_methods = [
bound_low,
precedence,
precedence_offset,
precedence_tight,
precedence_tight_offset,
alt_resources,
alt_resources_two
]

table = [[''] + [ '%s.%s' % (solve_method.__module__,solve_method.__name__) 
         for solve_method in solve_methods ] ]

for scenario_method in scenario_methods :
	scenario_name = scenario_method.__name__
	S,sols = scenario_method()
	row = [scenario_name]
	for solve_method in solve_methods :
		S_ = copy.deepcopy(S)
		try :
			if 'horizon' in solve_method.func_code.co_varnames :
				solve_method(S_,horizon=horizon)
			else :
				solve_method(S_)
			sol = str(S_.solution())
			valid = ( sol in sols )
			#if not valid :
			#	print(scenario_name,'%s.%s' % (solve_method.__module__,solve_method.__name__) )
			#	import pdb;pdb.set_trace()
			row.append(valid)
		except :
			row.append('na')
	table.append(row)

# write output
s = ''
for row in table :
	s +=  ','.join([ str(x) for x in row ]) + '\n'
print(s)
f = open('solvers.csv','w')
f.write(s)
f.close()




