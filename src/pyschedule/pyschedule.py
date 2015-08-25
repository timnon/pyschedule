#! /usr/bin/python
from __future__ import print_function

'''
Copyright 2015 Tim Nonner

Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''

"""
python package to formulate and solve resource-constrained scheduling problems
"""



from collections import OrderedDict as _DICT_TYPE
import types
import functools

try: # allow Python 2 vs 3 compatibility
	_maketrans = str.maketrans
except AttributeError:
	from string import maketrans as _maketrans

def _isnumeric(var) :
	"""
	Test if var is numeric, only integers are allowed
	"""
	return type(var) is int

def _isiterable(var) :
	"""
	Test if var is iterable
	"""
	return ( type(var) is list ) or ( type(var) is set ) or ( type(var) is tuple )

def alt(*args) :
	"""
	Method to reduce the given elements with the or-operator
	e.g. alt(R1,R2,R3) = alt( R for R in [R1,R2,R3] ) = alt([R1,R2,R3]) = R1|R2|R3
	"""
	l = [ functools.reduce(lambda x,y: x|y, a) for a in args if _isiterable(a)
	                                    or isinstance(a, types.GeneratorType)] +\
            [ a for a in args if not _isiterable(a) 
	                         and not isinstance(a, types.GeneratorType)  ]
	return functools.reduce(lambda x,y: x|y, l)



class _SchedElement(object):

	def __init__(self,name) :
		if type(name) is not str:
			raise Exception('ERROR: name %s is not a string'%str(name))
		trans = _maketrans("-+[] ->/","________")
		if name.translate(trans) != name:
			raise Exception('ERROR: name %s contains one of the following characters: -+[] ->/'%name)
		self.name = name

	def __str__(self) :
		return str(self.name)

	def __repr__(self) :
		return self.__str__()

	def __hash__(self) :
		return self.name.__hash__()



class _SchedElementAffine(_DICT_TYPE) :

	def __init__(self,unknown=None,element_class=_SchedElement,affine_operator='+') :
		_DICT_TYPE.__init__(self)
		self.element_class = element_class
		self.affine_operator = affine_operator
		if unknown == None :
			pass
		elif isinstance(unknown,self.element_class) :
			self[unknown] = 1
		elif _isnumeric(unknown) :
			self[1] = unknown
		elif isinstance(unknown,type(self)) :
			self.update(unknown)
		elif isinstance(unknown,list) :
			self.update(_DICT_TYPE(unknown))
		else :
			raise Exception('ERROR: cant init %s from %s' % (str(self),str(unknown)))

	def __add__(self,other) :
		if _isiterable(other) :
			return [ self + x for x in other ]
		if isinstance(other,type(self)) :
			new = type(self)(self)
			for key in other :
				if key in new :
					new[key] += other[key]
				else :
					new[key] = other[key]
			return new
		elif isinstance(other,self.element_class) or _isnumeric(other):
			return self + type(self)(other)
		raise Exception('ERROR: you cannot add %s to %s' % (str(other),str(self)))

	def __sub__(self,other) :
		if _isiterable(other) :
			return [ self - x for x in other ]
		if isinstance(other,type(self)) :
			new = type(self)(self)
			for key in other :
				if key in new :
					new[key] -= other[key]
				else :
					new[key] = -other[key]
			return new
		else :
			return self - type(self)(other)

	def __mul__(self,other) :
		if isinstance(other,type(self)) :
			new = type(self)(self)
			if 1 in other :
				for key in self :
					new[key] *= other[1]
			else :
				raise Exception('ERROR: multipy %s only with integer but not with %s'(str(self),str(other)))
			return new
		else :
			return self * type(self)(other)

	def __radd__(self,other) :
		return self + other

	def __repr__(self) :
		def format_coeff(val) :
			if val != 1 :
				return str(val)+'x'
			return ''
		return self.affine_operator.join([ format_coeff(self[key])+str(key) for key in self ])

	def __hash__(self) :
		return self.__repr__().__hash__()


	
class Scenario(_SchedElement):
	"""
	The base scenario class
	"""
	def __init__(self,name='scenario not named',horizon=None):
		_SchedElement.__init__(self,name)
		self.horizon = horizon
		self._tasks = _DICT_TYPE() #tasks
		self._resources = _DICT_TYPE() #resources
		self._constraints = list()

	def Task(self,name,length=1) :
		"""
		Adds a new task to the scenario
		name      : unique task name, must not contain special characters
    	length    : length of task, default is 1
		"""
		if name in self._tasks or name in self._resources:
			raise Exception('ERROR: resource or task with name %s already contained in scenario'%str(name))
		task = Task(name,length=length)
		self.add_task(task)
		return task

	def tasks(self,resource=None,single_resource=None) :
		"""
		Returns all tasks in scenario
		"""
		if resource is None :
			return list(self._tasks.values())
		else :
			return list({ T for RA in self.resources_req(resource=resource,single_resource=single_resource)
						    for T in RA.tasks() })

	def Resource(self,name,size=1) :
		"""
		Adds a new resource to the scenario
		name   : unique resource name, must not contain special characters
		size   : the size of the resource, if size > 1, then we get a cumulative resource that can process
		         different tasks in parallel
		"""
		if name in self._tasks or name in self._resources:
			raise Exception('ERROR: resource or task with name %s already contained in scenario'%str(name))
		resource = Resource(name,size=size)
		self.add_resource(resource)
		return resource

	def resources(self,task=None,single_resource=None) :
		"""
		Returns all resources in scenario
		"""
		if task is None :
			return list(self._resources.values())
		else :
			return list({ R for RA in self.resources_req(task=task,single_resource=single_resource) for R in RA })

	def solution(self) :
		"""
		Returns the last computed solution in tabular form with columns: task, resource, start, end
		"""
		solution = [ (T,R,T.start_value,T.start_value+T.length) \
                     for T in self.tasks() for R in T.resources ]
		solution = sorted(solution, key = lambda x : (x[2],str(x[0]),str(x[1])) ) # sort according to start and name
		return solution

	def objective(self):
		"""
		Returns a representation of all objectives
		"""
		tasks_objective = [T*T['_completion_time_cost'] for T in self.tasks() if '_completion_time_cost' in T ]
		if tasks_objective:
			return functools.reduce(lambda x,y:x+y,tasks_objective)
		return None

	def objective_value(self) :
		"""
		Returns the value of the objective
		"""
		return sum([ T['_completion_time_cost']*(T.start_value+T.length) for T in self.tasks()
		                                                                 if '_completion_time_cost' in T])

	def use_makespan_objective(self) :
		"""
		Set the objective to the makespan of all included tasks
		"""
		if 'MakeSpan' in self._tasks :
			self._constraints = [ C for C in self._constraints if self._tasks['MakeSpan'] not in C.tasks() ]
			del self._tasks['MakeSpan']
		tasks = self.tasks() # save tasks before adding makespan
		makespan = self.Task('MakeSpan')
		self += makespan % self.resources()[0] # add some random resource, every task needs one
		for T in tasks :
			self += T < makespan
		self.clear_objective()
		self += makespan*1

	def use_flowtime_objective(self) :
		"""
		Sets the objective to a uniform flow-time objective
		"""
		self.clear_objective()
		A = sum([ T*1 for T in self.tasks() ])
		del A[1] #remove 1 due to sum
		self += A

	def clear_solution(self):
		"""
		Remove the solution from the scenario
		"""
		for T in self.tasks() :
			T.start_value = None
			T.resources = None

	def clear_objective(self):
		"""
		Removes all objective annotations
		"""
		for T in self.tasks():
			if '_completion_time_cost' in T:
				del T['_completion_time_cost']

	def constraints(self,constraint_type=None):
		if constraint_type is None:
			return self._constraints
		return [ C for C in self._constraints if isinstance(C,constraint_type) ]

	def precs_lax(self):
		return self.constraints(PrecedenceLax)

	def precs_tight(self):
		return self.constraints(PrecedenceTight)

	def precs_cond(self):
		return self.constraints(PrecedenceCond)

	def bounds_low(self) :
		return self.constraints(BoundLow)

	def bounds_up(self) :
		return self.constraints(BoundUp)

	def bounds_low_tight(self) :
		return self.constraints(BoundLowTight)

	def bounds_up_tight(self) :
		return self.constraints(BoundUpTight)

	#TODO: add again last and first constraints
	'''
	def precs_first(self) :
		return [ C for C in self.constraints if isinstance(C,_Precedence) and C.kind == 'first' ]

	def precs_last(self) :
		return []#[ C for C in self.constraints if isinstance(C,_Precedence) and C.kind == 'last' ]
	'''

	def resources_req(self,task=None,resource=None,single_resource=None):
		"""
		Returns all resource requirements constraints. Restrict to constraints containing the given task or resource
		task:            only resource requirements that contain this task
		resource:        only resource requirements that contain this resource
		single_resource: True=only resource reqs. with a single resource,
		                 False=only resource reqs. with multiple resources
		"""
		constraints = self.constraints(ResourceReq)
		if task is not None :
			constraints = [ C for C in constraints 
                            if task in C.tasks() ]
		if resource is not None :
			constraints = [ C for C in constraints
                            if resource in C.resources() ]
		if single_resource is not None:
			if single_resource:
				constraints = [ C for C in constraints
                                if len(C.resources()) == 1 ]
			else:
				constraints = [ C for C in constraints 
                                if len(C.resources()) > 1 ]
		return constraints

	def resources_req_coeff(self,task,resource):
		"""
		Returns the maximum resource requirement of the given task on the given resource
		"""
		return max([ RA[resource] for RA in self.resources_req(task=task,resource=resource) ])

	def capacity_low(self):
		return self.constraints(CapacityLow)

	def capacity_up(self):
		return self.constraints(CapacityUp)

	def capacity_diff_up(self):
		return self.constraints(CapacityDiffUp)

	def capacity_diff_low(self):
		return self.constraints(CapacityDiffLow)

	def add_constraint(self,constraint):
		for task in constraint.tasks():
			if task not in self:
				raise Exception('ERROR: task %s is not contained in scenario %s'%(str(task.name),str(self.name)))
		for resource in constraint.resources():
			if resource not in self:
				raise Exception('ERROR: resource %s is not contained in scenario %s'%(str(resource.name),str(self.name)))
		if str(constraint) in [ str(C) for C in self._constraints ]:
			return self
		self._constraints.append(constraint)

	def remove_constraint(self,constraint):
		if str(constraint) not in [ str(C) for C in self._constraints ]:
			raise Exception('ERROR: constraint %s not contained in scenario %s'%(str(constraint),str(self.name)))
		self._constraints = [ C for C in self._constraints if str(C) != str(constraint) ]

	def add_task(self,task):
		if task.name in self._tasks and task is not self._tasks[task.name]:
			raise Exception('ERROR: task with name %s already contained in scenario %s' % (str(task.name),str(self.name)))
		elif task not in self.tasks():
			self._tasks[task.name] = task

	def remove_task(self,task):
		if task.name in self._tasks :
			del self._tasks[task.name]
		else :
			raise Exception('ERROR: task with name %s not contained in scenario %s' % (str(task.name),str(self.name)))
		self._constraints = [ C for C in self._constraints if task not in C.tasks() ]

	def add_task_affine(self,task_affine):
		for task in task_affine:
			if isinstance(task,Task):
				if task not in self:
					raise Exception('ERROR: task %s is not contained in scenario %s'%(str(task.name),str(self.name)))
			task.completion_time_cost = task_affine[task]

	def add_resource(self,resource):
		if resource.name in self._resources and resource is not self._resources[resource.name]:
			raise Exception('ERROR: resource with name %s already contained in scenario %s'%
			                (str(resource.name),str(self.name)))
		elif resource not in self.resources():
			self._resources[resource.name] = resource

	def remove_resource(self,resource):
		if resource.name in self._resources :
			del self._resources[resource.name]
		else:
			raise Exception('ERROR: resource with name %s not contained in scenario %s'%
			                (str(resource.name),str(self.name)))
		self._constraints = [ C for C in self._constraints if resource not in C.resources() ]

	def __iadd__(self,other) :
		if _isiterable(other) :
			for x in other :
				self += x
			return self
		elif isinstance(other,_Constraint) :
			self.add_constraint(other)
			return self
		elif isinstance(other,Task) :
			self.add_task(other)
			return self
		elif isinstance(other,_TaskAffine) :
			self.add_task_affine(other)
			return self
		elif isinstance(other,Resource) :
			self.add_resource(self,other)
			return self
		raise Exception('ERROR: cant add %s to scenario %s'%(str(other),str(self.name)))

	def __isub__(self,other) :
		if _isiterable(other):
			for x in other:
				self -= x
		elif isinstance(other,Task) :
			self.remove_task(other)
		elif isinstance(other,Resource):
			self.remove_resource(other)
		elif isinstance(other,_Constraint):
			self.remove_constraint(other)
		else:
			raise Exception('ERROR: task with name %s is not contained in scenario %s'%(str(other),str(self.name)))
		return self

	def __contains__(self, item):
		if isinstance(item,Task):
			return item in self._tasks.values()
		elif isinstance(item,Resource):
			return item in self._resources.values()
		else:
			raise Exception('ERROR: %s cannot be checked for containment in scenario %s'%(str(item),str(self.name)))
		return self

	def __iter__(self):
		return self._tasks.values().__iter__()

	def __getitem__(self, item):
		if item not in self._tasks and item not in self._resources:
			raise Exception('ERROR: task or resource with name %s is not contained in scenario %s'%
			                (str(item),str(self.name)))
		if item in self._tasks:
			return self._tasks[item]
		return self._resources[item]

	def check(self):
		"""
		Do basic checks on scenario
		"""
		# check if each task has a resource
		for T in self.tasks():
			if not self.resources(task=T):
				raise Exception('ERROR: task %s has no resource requirement'%str(T))

	def __str__(self) :
		s = '###############################################\n'
		s += '\n'
		s += 'SCENARIO: '+self.name
		if self.horizon is not None:
			s += ' / horizon: %i\n\n'%self.horizon
		else:
			s += ' / no horizon set\n\n'

		s += 'OBJECTIVE: '+str(self.objective())+'\n\n'

		s += 'RESOURCES:\n'
		for R in self.resources() :
			s += str(R.name)+'\n'
		s += '\n'

		s += 'TASKS:\n'
		for T in self.tasks() :
			s += '%s : %s\n'%(str(T.name),str(self.resources_req(task=T)))
		s += '\n'

		def print_constraint(title,constraints):
			s = ''
			if constraints:
				s += '%s:\n'%title
				s += '\n'.join([ C.__repr__() for C in constraints ]) + '\n'
				s += '\n'
			return s
		s += print_constraint('LAX PRECEDENCES',self.precs_lax())
		s += print_constraint('TIGHT PRECEDENCES',self.precs_tight())
		s += print_constraint('COND PRECEDENCES',self.precs_cond())
		s += print_constraint('LOWER BOUNDS',self.bounds_low())
		s += print_constraint('UPPER BOUNDS',self.bounds_up())
		s += print_constraint('TIGHT LOWER BOUNDS',self.bounds_low_tight())
		s += print_constraint('TIGHT UPPER BOUNDS',self.bounds_up_tight())
		s += print_constraint('CAPACITY LOWER BOUNDS',self.capacity_low())
		s += print_constraint('CAPACITY UPPER BOUNDS',self.capacity_up())
		s += print_constraint('CAPACITY DIFF LOWER BOUNDS',self.capacity_diff_low())
		s += print_constraint('CAPACITY DIFF UPPER BOUNDS',self.capacity_diff_up())
		s += '###############################################'
		return s



class Task(_SchedElement) :
	"""
	A task to be processed by at least one resource
	"""

	def __init__(self,name,length=1) :
		_SchedElement.__init__(self,name)
		if not _isnumeric(length):
			raise Exception('ERROR: task length must be an integer')
		self.length = length
		self.start_value = None # should be filled by solver
		self.resources = None # should be filled by solver
		self.completion_time_cost = None # cost on the final completion time
		self.group = None # group exchangeable tasks

	def __len__(self) :
		return self.length

	def __lt__(self,other) :
		return _TaskAffine(self) < other

	def __gt__(self,other) :
		return _TaskAffine(self) > other

	def __le__(self,other) :
		return _TaskAffine(self) <= other

	def __ge__(self,other) :
		return _TaskAffine(self) >= other

	def __ne__(self,other) :
		return _TaskAffine(self) != other

	def __lshift__(self,other) :
		return _TaskAffine(self) << other

	def __rshift__(self,other) :
		return _TaskAffine(self) >> other

	def __add__(self,other) :
		return _TaskAffine(self) + other

	def __sub__(self,other) :
		return _TaskAffine(self) - other

	def __mul__(self,other) :
		return _TaskAffine(self) * other

	def __radd__(self,other) :
		return _TaskAffine(self) + other

	def __mod__(self,other) :
		if _isiterable(other) :
			return [ x % self for x in other ]
		return other % self

	def __contains__(self,key):
		if not hasattr(self,key):
			return False
		if getattr(self,key) is None:
			return False
		return True



class _TaskAffine(_SchedElementAffine) :

	def __init__(self,unknown=None) :
		_SchedElementAffine.__init__(self,unknown=unknown,element_class=Task)

	def _get_prec(self,TA,comp_operator) :
		pos_tasks = [ T for T in TA if isinstance(T,Task) and TA[T] >= 0 ]
		neg_tasks = [ T for T in TA if isinstance(T,Task) and TA[T] < 0 ]
		if len(neg_tasks) > 1 or len(pos_tasks) > 1 :
			raise Exception('ERROR: can only deal with simple precedences of \
									the form T1 + 3 < T2 or T1 < 3 and not %s'%str(TA) )
		# get offset
		offset = 0
		if 1 in TA :
			offset = TA[1]
		if pos_tasks and neg_tasks :
			left = pos_tasks[0]
			right = neg_tasks[0]
			if comp_operator == '<' :
				return PrecedenceLax(task_left=left,task_right=right,offset=offset)
			elif comp_operator == '<=' :
				return PrecedenceTight(task_left=left,task_right=right,offset=offset)
			elif comp_operator == '<<' :
				return PrecedenceCond(task_left=left,task_right=right,offset=offset)
		elif pos_tasks and not neg_tasks:
			left = pos_tasks[0]
			right = -offset
			if comp_operator == '<':
				return BoundUp(task=left,bound=right)
			elif comp_operator == '<=':
				return BoundUpTight(task=left,bound=right)
			elif comp_operator == '>':
				return BoundLow(task=left,bound=right)
			elif comp_operator == '>=':
				return BoundLowTight(task=left,bound=right)
		elif neg_tasks and not pos_tasks:
			left = neg_tasks[0]
			right = offset
			if comp_operator == '<':
				return BoundLow(task=left,bound=right)
			elif comp_operator == '<=':
				return BoundLowTight(task=left,bound=right)
			elif comp_operator == '>':
				return BoundUp(task=left,bound=right)
			elif comp_operator == '>=':
				return BoundUpTight(task=left,bound=right)
		raise Exception('ERROR: sth is wrong')

	def __lt__(self,other) :
		if _isiterable(other) :
			return [ self < x for x in other ]
		if not isinstance(other,type(self)) :
			return self < _TaskAffine(other)
		return self._get_prec(self-other,'<')

	def __gt__(self,other) :
		if _isiterable(other) :
			return [ self > x for x in other ]
		if not isinstance(other,type(self)) :
			return self > _TaskAffine(other)
		return _TaskAffine(other) < self

	def __le__(self,other) :
		if _isiterable(other) :
			return [ self <= x for x in other ]
		if not isinstance(other,type(self)) :
			return self <= _TaskAffine(other)
		return self._get_prec(self-other,'<=')

	def __ge__(self,other) :
		if _isiterable(other) :
			return [ self >= x for x in other ]
		if not isinstance(other,type(self)) :
			return self >= _TaskAffine(other)
		return _TaskAffine(other) <= self

	def __lshift__(self,other) :
		if _isiterable(other) :
			return [ self << x for x in other ]
		if not isinstance(other,type(self)) :
			return self << _TaskAffine(other)
		return self._get_prec(self-other,'<<')

	def __rshift__(self,other) :
		if _isiterable(other) :
			return [ self >> x for x in other ]
		if not isinstance(other,type(self)) :
			return self >> _TaskAffine(other)
		return _TaskAffine(other) << self



class _Constraint(_SchedElement) :

	def __init__(self) :
		_SchedElement.__init__(self,name='')

	def tasks(self):
		return []

	def resources(self):
		return []



class _Bound(_Constraint) :

	def __init__(self,task,bound) :
		_Constraint.__init__(self)
		self.task = task
		self.bound = bound
		self.comp_operator = '<'

	def tasks(self) :
		return [self.task]

	def __repr__(self) :
		return str(self.task) + ' ' + str(self.comp_operator) + ' ' + str(self.bound)

	def __str__(self) :
		return self.__repr__()

	def __hash__(self) :
		return self.__repr__().__hash__()



class BoundLow(_Bound) :
	"""
	A bound of the form T > 3
	"""
	def __init__(self,task,bound) :
		_Bound.__init__(self,task,bound)
		self.comp_operator = '>'



class BoundUp(_Bound) :
	"""
	A bound of the form T < 3
	"""
	def __init__(self,task,bound) :
		_Bound.__init__(self,task,bound)
		self.comp_operator = '<'



class BoundLowTight(_Bound) :
	"""
	A bound of the form T >= 3
	"""
	def __init__(self,task,bound) :
		_Bound.__init__(self,task,bound)
		self.comp_operator = '>='



class BoundUpTight(_Bound) :
	"""
	A bound of the form T <= 3
	"""
	def __init__(self,task,bound) :
		_Bound.__init__(self,task,bound)
		self.comp_operator = '<='



class _Precedence(_Constraint) :
	"""
	A precedence constraint of two tasks, left and right, and an offset.
	"""
	def __init__(self,task_left,task_right,offset=0) :
		_Constraint.__init__(self)
		self.task_left = task_left
		self.task_right = task_right
		self.offset = offset
		self.comp_operator = '<'

	def tasks(self) :
		return [self.task_left,self.task_right]

	def __repr__(self) :
		s = str(self.task_left) + ' '
		if self.offset > 0 :
			s += '+ ' + str(self.offset) + ' '
		s += str(self.comp_operator) + ' ' + str(self.task_right)
		if self.offset < 0 :
			s += ' + ' + str(-self.offset) + ' '
		return s

	def __str__(self) :
		return self.__repr__()

	def __hash__(self) :
		return self.__repr__().__hash__()



class PrecedenceLax(_Precedence) :
	"""
	A precedence of the form T1 + 3 < T2
	"""
	def __init__(self,task_left,task_right,offset=0) :
		_Precedence.__init__(self,task_left,task_right,offset)
		self.comp_operator = '<'



class PrecedenceTight(_Precedence) :
	"""
	A precedence of the form T1 + 3 <= T2
	"""
	def __init__(self,task_left,task_right,offset=0) :
		_Precedence.__init__(self,task_left,task_right,offset)
		self.comp_operator = '<='



class PrecedenceCond(_Precedence) :
	"""
	A precedence of the form T1 + 3 <= T2
	"""
	def __init__(self,task_left,task_right,offset=0) :
		_Precedence.__init__(self,task_left,task_right,offset)
		self.comp_operator = '<<'




class Resource(_SchedElement) :
	"""
	A resource which can process at most one task per time step
	"""

	def __init__(self,name=None,size=1) :
		_SchedElement.__init__(self,name)
		self.size = size

	def __iadd__(self,other) :
		if isinstance(other,Task) :
			other += self
			return self
		elif _isiterable(other) :
			for x in other : self += x	
		else :
			raise Exception('ERROR: cant add '+str(other)+' to resource '+str(self))
		return self

	def __mul__(self,other) :
		return _ResourceAffine(self) * other

	def __or__(self,other) :
		if isinstance(other,ResourceReq) :
			other._resources = self | other._resources
			return other
		return _ResourceAffine(self) | other

	def __mod__(self,other) :
		return _ResourceAffine(self) % other

	def __getitem__(self, key):
		C = _Capacity(resource=self)
		if isinstance(key,slice) or isinstance(key,int):
			return C[key]
		elif isinstance(key,str):
			C.param = key
			return C
		raise Exception('ERROR: index not correct')

	def __le__(self,other):
		return _Capacity(resource=self) <= other

	def __ge__(self,other):
		return _Capacity(resource=self) >= other

	def __invert__(self):
		return _Capacity(resource=self,diff=True)



class _ResourceAffine(_SchedElementAffine) :

	def __init__(self,unknown=None) :
		_SchedElementAffine.__init__(self,unknown=unknown,element_class=Resource,affine_operator='|')

	def __or__(self,other) :
		return super(_ResourceAffine,self).__add__(_ResourceAffine(other)) #add of superclass

	def __mod__(self,other) :
		RA = ResourceReq(tasks=[], resources=self)
		return RA % other



class ResourceReq(_Constraint) :
	"""
	A resource requirement of one or multiple tasks
	"""
	def __init__(self,tasks,resources):
		_Constraint.__init__(self)
		self._tasks = tasks
		self._resources = resources

	def tasks(self) :
		return self._tasks

	def resources(self):
		return list(self)

	def __getitem__(self, resource):
		if resource in self._resources :
			try :
				return self._resources.__getitem__(resource)
			except :
				return 1
		raise Exception('ERROR: %s not contained in %s' % (str(resource),str(self)))

	def __iter__(self):
		return self._resources.__iter__()

	def __or__(self,other) :
		if _isiterable(other) :
			for x in other :
				self = self | other
		if isinstance(other,Resource) or isinstance(other,_ResourceAffine) :
			self._resources = self._resources | other
		else :
			Exception('ERROR: cannot take or of %s with resource requirement %s' % (str(other),str(self)))
		return self

	def __mod__(self,other) :
		if not _isiterable(other):
			other = [other]
		for x in other :
			if isinstance(x,Task) :
				self._tasks.append(x)
			else :
				raise Exception('ERROR: cannot add %s to resource requirement %s' % (str(x),str(self)))
		return self

	def __repr__(self):
		s = ''
		if len(self.tasks()) > 1 :
			s += '('
		s += ','.join([ str(T) for T in self.tasks() ])
		if len(self.tasks()) > 1 :
			s += ')'
		s += ' % ' + str(self._resources)
		return s

	def __str__(self):
		return self.__repr__()



class _Capacity(_Constraint):

	def __init__(self,resource,param='length',bound=None,start=None,end=None,comp_operator=None,diff=False):
		_Constraint.__init__(self)
		self.resource = resource
		self.param = param
		self.start = start
		self.end = end
		self.bound = bound
		self.comp_operator = comp_operator
		self.diff = diff

	def __ge__(self, other):
		if not _isnumeric(other):
			raise Exception('ERROR: %s is not an integer, only integers are allowed'%str(other))
		self.__class__ = CapacityLow
		if self.diff:
			self.__class__ = CapacityDiffLow
		self.comp_operator = '>='
		self.bound = other
		return self

	def __le__(self, other):
		if not _isnumeric(other):
			raise Exception('ERROR: %s is not an integer, only integers are allowed'%str(other))
		self.__class__ = CapacityUp
		if self.diff:
			self.__class__ = CapacityDiffUp
		self.comp_operator = '<='
		self.bound = other
		return self

	def __getitem__(self,key):
		if isinstance(key,int):
			self.start = key
			self.end = key+1
			return self
		elif isinstance(key,slice):
			self.start = key.start
			self.end = key.stop
			return self
		raise Exception('ERROR: index is wrong')

	def __invert__(self):
		self.diff = not self.diff
		return self

	def __str__(self):
		slice = ''
		if self.start is not None or self.end is not None:
			slice = '['
			if self.start is not None:
				slice += str(self.start)
			slice += ':'
			if self.end is not None: #large number
				slice += str(self.end)
			slice += ']'
		s = '%s[\'%s\']%s %s %s' % (str(self.resource),str(self.param),slice,str(self.comp_operator),str(self.bound))
		if self.diff:
			s = '~'+s
		return s

	def __repr__(self):
		return self.__str__()



class CapacityLow(_Capacity):
	"""
	A lower capacity bound on one resource in an interval
	"""
	def __init__(self,resource,param='length',bound=None,start=None,end=None):
		_Capacity.__init__(self,resource,param,bound,start,end,comp_operator='>=')



class CapacityDiffLow(_Capacity):
	"""
	A lower bound on the number of on/off-switches for the capacity
	"""
	def __init__(self,resource,param='length',bound=None,start=None,end=None):
		_Capacity.__init__(self,resource,param,bound,start,end,comp_operator='<<')



class CapacityUp(_Capacity):
	"""
	An upper capacity bound on one resource in an interval
	"""
	def __init__(self,resource,param='length',bound=None,start=None,end=None):
		_Capacity.__init__(self,resource,param,bound,start,end,comp_operator='<=')



class CapacityDiffUp(_Capacity):
	"""
	An upper bound on the number of on/off-switches for the capacity
	"""
	def __init__(self,resource,param='length',bound=None,start=None,end=None):
		_Capacity.__init__(self,resource,param,bound,start,end,comp_operator='<<')






















