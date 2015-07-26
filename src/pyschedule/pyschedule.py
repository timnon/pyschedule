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

#TODO: resources requirements should not overlap (can they?)
#TODO: cpoptimier with cond precedence constraints
#TODO: tasks of length 0 dont seem to work???


from collections import OrderedDict as _DICT_TYPE

try: # allow Python 2 vs 3 compatibility
	_maketrans = str.maketrans
except AttributeError:
	from string import maketrans as _maketrans

def OR(L) :
	"""
	method to iterate the or-operator over a list to allow lists of alternative resources,
        e.g. OR([R1,R2,R3]) = R1 | R2 | R3
	"""
	x = None
	if L :
		x = L[0]
	for y in L[1:] :
		x = x | y
	return x

def _isnumeric(var) :
	return isinstance(var,(int)) # only integers are accepted

def _isiterable(var) :
	return ( type(var) is list ) or ( type(var) is set ) or ( type(var) is tuple )



class _SchedElement(object) : # extend string object

	def __init__(self,name,numeric_name_prefix='E') :
		# purely numeric names are not allowed
		if _isnumeric(name) :
			name = numeric_name_prefix+str(name)
		# remove illegal characters
		trans = _maketrans("-+[] ->/","________")
		self.name = str(name).translate(trans)

	def __repr__(self) :
		return self.name

	def __str__(self) :
		return self.name

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
			raise Exception('ERROR: cant init '+str(self)+' from '+str(unknown))

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
		else :
			new = type(self)(other)
			return self + new

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
				raise Exception('ERROR: multipy '+str(self)+' only with number \
                                                 but not with '+str(other))
			return new
		else :
			return self * type(self)(other)

	def __radd__(self,other) :
		return self + other

	def __repr__(self) :
		def format_coeff(val) :
			if val != 1 :
				return str(val)+'x'
			else :
				return ''
		# TODO: do not plot constant if not necessary
		return (' '+self.affine_operator+' ').join([ format_coeff(self[key])+str(key) for key in self ])

	def __hash__(self) :
		return self.__repr__().__hash__()


	
class Scenario(_SchedElement):
	
	def __init__(self,name='scenario not named') :
		_SchedElement.__init__(self,name,numeric_name_prefix='S')
		self.objective = _TaskAffine()
		self.T = _DICT_TYPE() #tasks
		self.R = _DICT_TYPE() #resources
		self.constraints = list()

		# parameters
		#self.is_same_resource_precs_lax = False
		#self.is_same_resource_precs_tight = False

	def Task(self,name,length=1,start=None,resources=None,cost=None,capacity_req=None) :
		"""
		Adds a task with the given name to the scenario. Task names need to be unique.
		"""
		T = Task(name,length=length,cost=cost,start=start,resources=resources,capacity_req=capacity_req)
		if str(T) not in self.T :
			self.T[str(T)] = T
		else :
			raise Exception('ERROR: task with name '+str(T)+' already contained in scenario '+str(self))
		return T

	def tasks(self,resource=None) :
		if resource is None :
			return list(self.T.values())
		else :
			return list({ T for RA in self.resources_req(resource=resource) for T in RA.tasks() })

	def Resource(self,name,size=1,capacity=None,cost=None) :
		"""
		Adds a resource with the given name to the scenario. Resource names need to be unique.
		"""
		R = Resource(name,size=size,capacity=capacity,cost=cost)
		if str(R) not in self.R : #[ str(R_) for R_ in self.resources ] :
			self.R[str(R)] = R #.append(R)
		else :
			raise Exception('ERROR: resource with name '+str(R)+' already contained in scenario '+str(self))
		return R

	def resources(self,task=None) :
		if task is None :
			return list(self.R.values())
		else :
			return list({ R for RA in self.resources_req(task=task) for R in RA })

	def solution(self) :
		"""
		Returns the last computed solution in tabular form with columns: task, resource, start, end
		"""
		solution = [ (T,R,T.start,T.start+T.length) \
                             for T in self.tasks() for R in T.resources ]
		solution = sorted(solution, key = lambda x : (x[2],str(x[0]),str(x[1])) ) # sort according to start and name
		return solution

	def objective_value(self) :
		"""
		Returns the value of the objective
		"""
		return sum([ self.objective[T]*(T.start+T.length) for T in self.objective ])

	def use_makespan_objective(self) :
		"""
		Set the objective to the makespan of all included tasks without a fixed start
		"""
		if 'MakeSpan' in self.T :
			del self.T['MakeSpan']
		tasks = self.tasks() # save tasks before adding makespan
		makespan = self.Task('MakeSpan')
		self += makespan % self.resources()[0] # add some random resource, every task needs one
		for T in tasks :
			#TODO: what for T.start is not None???
			self += T < makespan
		self.objective.clear()
		self += makespan*1

	def use_flowtime_objective(self) :
		"""
		Sets the objective a uniform flow-time objective
		"""
		self.objective.clear()
		self += sum([ T*1 for T in self.tasks() if T.start is None ])

	def clear_task_starts(self) :
		"""
		Remove the start times of all tasks
		"""
		for T in self.tasks() :
			T.start = None

	def precs_lax(self) :
		return [ C for C in self.constraints if isinstance(C,PrecedenceLax) ]

	def precs_tight(self) :
		return [ C for C in self.constraints if isinstance(C,PrecedenceTight)  ]
		
	def precs_cond(self) :
		return [ C for C in self.constraints if isinstance(C,PrecedenceCond) ]

	def precs_low(self) :
		return [ C for C in self.constraints if isinstance(C,PrecedenceLow) ]

	def precs_up(self) :
		return [ C for C in self.constraints if isinstance(C,PrecedenceUp) ]

	#TODO: add again last and first constraints
	'''
	def precs_first(self) :
		return [ C for C in self.constraints if isinstance(C,_Precedence) and C.kind == 'first' ]

	def precs_last(self) :
		return []#[ C for C in self.constraints if isinstance(C,_Precedence) and C.kind == 'last' ]
	'''

	def resources_req(self,task=None,resource=None):
		"""
		Returns all resource requirements constraints. Restrict to constraints containing the given task or resource
		"""
		Cs = [ C for C in self.constraints if isinstance(C,ResourceReq) ]
		if task is not None :
			Cs = [ C for C in Cs if task in C.tasks() ]
		if resource is not None :
			Cs = [ C for C in Cs if resource in C.resources() ]
		return Cs

	def resources_req_coeff(self,task,resource):
		"""
		Returns the maximum resource requirement of the given task on the given resource
		"""
		return max([ RA[resource] for RA in self.resources_req(task=task,resource=resource) ])

	def add_constraint(self,constraint):
		self.constraints.append(constraint)
		return self

	def add_task(self,task):
		if task.name in self.T :
			raise Exception('ERROR: task '+str(task)+' already contained in scenario '+str(self))
		self.T[task.name] = task

	def add_task_affine(self,task_affine):
		self.objective += task_affine

	def add_resource(self,resource):
		if resource.name in self.R :
			raise Exception('ERROR: resource '+str(resource)+' already contained in scenario '+str(self))
		self.R[resource.name] = resource

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
		raise Exception('ERROR: cant add '+str(other)+' to scenario '+str(self))

	# TODO: create more complete removal method
	def __isub__(self,other) :
		if isinstance(other,Task) :
			if other.name in self.T :
				del self.T[other.name]
			else :
				raise Exception('ERROR: task with name '+str(other.name)+\
                                ' is not contained in scenario '+str(self))
		return self

	def __repr__(self) :
		s = '\n##############################################\n\n'
		s += 'SCENARIO: '+str(self)+'\n\n'
		#print objective
		s += 'OBJECTIVE: '+str(self.objective)+'\n\n'

		s += 'RESOURCES:\n'
		for R in self.resources() :
			s += str(R)+'\n'
		s += '\n'
		# print tasks
		s += 'TASKS:\n'
		for T in self.tasks() :
			s += str(T)
			if T.start is not None :
				s += ' at ' + str(T.start)
			if T.resources :
				s += ' on ' + str(T.resources)
			s += ' : ' + str(self.resources_req(task=T)) + '\n'
		s += '\n'
		#s += '\n'.join([ str(T)+' : '+ str(T.resources_req) for T in sorted(self.tasks()) ]) + '\n\n'
		# print resources

		if self.precs_lax() :
			# print precedences
			s += 'PRECEDENCES:\n'
			s += '\n'.join([ P.__repr__() for P in self.precs_lax() ]) + '\n'
			s += '\n'

		if self.precs_tight() :
			# print precedences
			s += 'TIGHT PRECEDENCES:\n'
			s += '\n'.join([ P.__repr__() for P in self.precs_tight() ]) + '\n'
			s += '\n'

		if self.precs_cond() :
			# print precedences
			s += 'COND PRECEDENCES:\n'
			s += '\n'.join([ P.__repr__() for P in self.precs_cond() ]) + '\n'
			s += '\n'

		if self.precs_low() :
			# print precedences
			s += 'LOWER BOUNDS:\n'
			s += '\n'.join([ P.__repr__() for P in self.precs_low() ]) + '\n'
			s += '\n'

		if self.precs_up() :
			# print precedences
			s += 'UPPER BOUNDS:\n'
			s += '\n'.join([ P.__repr__() for P in self.precs_up() ]) + '\n'
			s += '\n'

		'''
		if self.precs_first() :
			# print precedences
			s += 'FIRST TASKS:\n'
			s += '\n'.join([ P.__repr__() for P in self.precs_first() ]) + '\n'
			s += '\n'

		if self.precs_last() :
			# print precedences
			s += 'LAST TASKS:\n'
			s += '\n'.join([ P.__repr__() for P in self.precs_last() ]) + '\n'
			s += '\n'
		'''

		s += '##############################################\n'
		return s



class Task(_SchedElement) :
	"""
	A task to be processed by at least one resource
	"""

	def __init__(self,name,length=1,cost=None,start=None,resources=None,resources_req=None,capacity_req=None) :
		_SchedElement.__init__(self,name,numeric_name_prefix='T')
		self.length = length
		self.start = start
		self.resources = resources
		if capacity_req is not None :
			self.capacity_req = capacity_req
		else :
			self.capacity_req = self.length

	def __len__(self) :
		return self.length

	def __lt__(self,other) :
		'''
		if isinstance(other,Resource) :
			return Precedence(left=self,right=other,kind='first')
		'''
		return _TaskAffine(self) < other

	def __gt__(self,other) :
		'''
		if isinstance(other,Resource) :
			return _Precedence(left=self,right=other,kind='last')
		'''
		return _TaskAffine(self) > other

	def __le__(self,other) :
		return _TaskAffine(self) <= other

	def __ge__(self,other) :
		return _TaskAffine(self) <= other

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



class _TaskAffine(_SchedElementAffine) :

	def __init__(self,unknown=None) :
		_SchedElementAffine.__init__(self,unknown=unknown,element_class=_SchedElement)

	def _get_prec(self,TA,comp_operator) :
		pos_tasks = [ T for T in TA if isinstance(T,Task) and TA[T] >= 0 ]
		neg_tasks = [ T for T in TA if isinstance(T,Task) and TA[T] < 0 ]
		if len(neg_tasks) > 1 or len(pos_tasks) > 1 :
			raise Exception('ERROR: can only deal with simple precedences of \
									the form T1 + 3 < T2 or T1 < 3 and not '+str(TA) )
		# get offset
		offset = 0
		if 1 in TA : offset = TA[1]

		if pos_tasks and neg_tasks :
			left = pos_tasks[0]
			right = neg_tasks[0]
			if comp_operator == '<' :
				return PrecedenceLax(left=left,right=right,offset=offset)
			elif comp_operator == '<=' :
				return PrecedenceTight(left=left,right=right,offset=offset)
			elif comp_operator == '<<' :
				return PrecedenceCond(left=left,right=right,offset=offset)
		elif pos_tasks and not neg_tasks :
			left = pos_tasks[0]
			right = -offset
			return PrecedenceUp(left=left,right=right)
			return self
		elif not pos_tasks and neg_tasks :
			left = neg_tasks[0]
			right = offset
			return PrecedenceLow(left=left,right=right)

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
	"""
	An arbitrary constraint
	"""
	def __init__(self) :
		_SchedElement.__init__(self,name='',numeric_name_prefix='C')

	def tasks(self):
		return []

	def resources(self):
		return []



class _Precedence(_Constraint) :
	"""
	A precedence constraint of two tasks, left and right, and an offset.
	right might also be a number.
	"""
	def __init__(self,left=None,right=None,offset=0,TA=None) :
		_Constraint.__init__(self)
		if left is not None and right is not None :
			self.left = left
			self.right = right
			self.offset = offset
			self.comp_operator = '<'
		elif TA is not None :
			self.format(TA)

	def tasks(self) :
		return [self.left,self.right]

	def __repr__(self) :
		#kind_to_comp_operator = { 'lax':'<', 'tight':'<=', 'cond':'<<', 'low':'>', 'up':'<', 'first':'<', 'last':'>' }
		s = str(self.left) + ' '
		if self.offset != 0 :
			s += '+ ' + str(self.offset) + ' '
		s += str(self.comp_operator) + ' ' + str(self.right)
		return s

	def __str__(self) :
		return self.__repr__()

	def __hash__(self) :
		return self.__repr__().__hash__()



class PrecedenceLow(_Precedence) :
	"""
	A precedence of the form T1 + 3 < T2
	"""
	def __init__(self,left,right,offset=0) :
		_Precedence.__init__(self,left,right,offset)
		self.comp_operator = '>'



class PrecedenceUp(_Precedence) :
	"""
	A precedence of the form T1 + 3 < T2
	"""
	def __init__(self,left,right,offset=0) :
		_Precedence.__init__(self,left,right,offset)
		self.comp_operator = '<'



class PrecedenceLax(_Precedence) :
	"""
	A precedence of the form T1 + 3 < T2
	"""
	def __init__(self,left,right,offset=0) :
		_Precedence.__init__(self,left,right,offset)
		self.comp_operator = '<'



class PrecedenceTight(_Precedence) :
	"""
	A precedence of the form T1 + 3 <= T2
	"""
	def __init__(self,left,right,offset=0) :
		_Precedence.__init__(self,left,right,offset)
		self.comp_operator = '<='



class PrecedenceCond(_Precedence) :
	"""
	A precedence of the form T1 + 3 <= T2
	"""
	def __init__(self,left,right,offset=0) :
		_Precedence.__init__(self,left,right,offset)
		self.comp_operator = '<='




class Resource(_SchedElement) :
	"""
	A resource which can process at most one task per time step

	capacity :  minimal and maximal task capacity of the tuple form (min,max)
                    if capacity is an integer then this is interpreted as the
                    maximal task capacity and the minimal taks capacity is set to 0
	cost : the cost of using this resource in the solution
	"""

	def __init__(self,name=None,size=1,capacity=None,cost=None) :
		_SchedElement.__init__(self,name,numeric_name_prefix='R')
		self.size = size
		self.capacity = capacity
		self.cost = cost

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

	'''
	# iteration over resource gives the resource to simplify
	# the construction of solvers
	def __iter__(self) :
		return _ResourceAffine(self).__iter__()

	# necessary to allow capacity check to simplify
	# the construction of solvers
	def __getitem__(self,index) :
		if index == self :
			return 1
		else :
			raise Exception('ERROR: resource '+str(self)+' can only return its own capacity')
	'''



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
		s = str(self._resources) + ' % '
		if len(self.tasks()) > 1 :
			s += '('
		s += ','.join([ str(T) for T in self.tasks() ])
		if len(self.tasks()) > 1 :
			s += ')'
		return s

	def __str__(self):
		return self.__repr__()
















