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
	method to iterate the or-operator over a list to allow lists of alternative resources, e.g. OR([R1,R2,R3]) = R1 | R2 | R3
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
		#self.objective_price = _ResourceAffine() #TODO: add more complex objective

		# parameters
		self.is_same_resource_precs_lax = False
		self.is_same_resource_precs_tight = False

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

	def tasks(self) :
		return list(self.T.values())

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

	def resources(self) :
		return list(self.R.values())

	def R(self,name) :
		return self._resources[name]

	def solution(self) :
		"""
		Returns the last computed solution in tabular form with columns: task, resource, start, end
		"""
		solution = [ (T,R,T.start,T.start+T.length) \
                             for T in self.tasks() for R in T.resources ]
		solution += [ (T,'',T.start,T.start+T.length) \
                             for T in self.tasks() if not T.resources ]
		solution = sorted(solution, key = lambda x : (x[2],x[0]) ) # sort according to start and name
		return solution

	def use_makespan_objective(self) :
		"""
		Set the objective to the makespan of all included tasks without a fixed start
		"""
		tasks = self.tasks() # save tasks before adding makespan
		makespan = self.Task('MakeSpan',cost=1)
		makespan += self.resources()[0] # add some random resource, every task needs one
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
		return [ C for C in self.constraints if isinstance(C,Precedence) and C.kind == 'lax' ]

	def precs_tight(self) :
		return [ C for C in self.constraints if isinstance(C,Precedence) and C.kind == 'tight' ]
		
	def precs_cond(self) :
		return [ C for C in self.constraints if isinstance(C,Precedence) and C.kind == 'cond' ]

	def precs_low(self) :
		return [ C for C in self.constraints if isinstance(C,Precedence) and C.kind == 'low' ]

	def precs_up(self) :
		return [ C for C in self.constraints if isinstance(C,Precedence) and C.kind == 'up' ]

	def precs_first(self) :
		return [ C for C in self.constraints if isinstance(C,Precedence) and C.kind == 'first' ]

	def precs_last(self) :
		return [ C for C in self.constraints if isinstance(C,Precedence) and C.kind == 'last' ]

	def __iadd__(self,other) :
		if _isiterable(other) :
			for x in other : self += x
			return self

		elif isinstance(other,_TaskAffineConstraint) :
			pos_tasks = [ T for T in other if isinstance(T,Task) and other[T] >= 0 ]
			neg_tasks = [ T for T in other if isinstance(T,Task) and other[T] < 0 ]
			if len(neg_tasks) > 1 or len(pos_tasks) > 1 :
				raise Exception('ERROR: can only deal with simple precedences of \
		                                 the form T1 + 3 < T2 or T1 < 3 and not '+str(other) )
			# get offset
			offset = 0
			if 1 in other : offset = other[1]

			if pos_tasks and neg_tasks :
				left = pos_tasks[0]
				right = neg_tasks[0]
				if other.comp_operator == '<' :
					self.constraints.append(Precedence(left=left,right=right,offset=offset,kind='lax'))
				elif other.comp_operator == '<=' :
					self.constraints.append(Precedence(left=left,right=right,offset=offset,kind='tight'))
				elif other.comp_operator == '<<' :
					shared_resources = list( set(left.resources_req_list()) & set(right.resources_req_list()) )
					prec = Precedence(left=left,right=right,offset=offset,kind='cond')
					if not shared_resources :
						raise Exception('ERROR: tried to add precedence '+str(prec)+' but tasks dont compete for resources')
					self.constraints.append(prec)
				return self
			elif pos_tasks and not neg_tasks :
				left = pos_tasks[0]
				right = -offset
				self.constraints.append(Precedence(left=left,right=right,kind='up'))
				return self
			elif not pos_tasks and neg_tasks :
				left = neg_tasks[0]
				right = offset
				self.constraints.append(Precedence(left=left,right=right,kind='low'))
				return self
			raise Exception('ERROR: cannot add constraint '+str(other)+' to scenario')

		elif isinstance(other,Precedence) :
			self.constraints.append(other)
			return self

		elif isinstance(other,Task) :
			if other.name in self.T :
				raise Exception('ERROR: task with name '+str(other.name)+' already contained in scenario '+str(self))
			self.T[other.name] = other
			return self

		elif isinstance(other,_TaskAffine) :
			self.objective += other
			return self

		elif isinstance(other,Resource) :
			if other.name in self.R :
				raise Exception('ERROR: resource with name '+str(T)+' already contained in scenario '+str(self))
			self.R[other.name] = other
			return self

		'''
		elif isinstance(other,_ResourceAffine) :
			self.objective_price += other
			return self
		'''

		raise Exception('ERROR: cant add '+str(other)+' to scenario '+str(self))

	def __isub__(self,other) :
		if isinstance(other,Task) :
			if other.name in self.T :
				del self.T[other.name]
			else :
				raise Exception('ERROR: task with name '+str(other.name)+' is not contained in scenario '+str(self))
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
			s += ' : ' + str(list(T)) + '\n'
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

		s += '##############################################\n'
		return s



class Task(_SchedElement) :
	"""
	A task to be processed by at least one resource
	"""

	def __init__(self,name,length=1,cost=None,start=None,resources=None,resources_req=None,capacity_req=None) :
		_SchedElement.__init__(self,name,numeric_name_prefix='T')
		self.length = length
		self.cost = cost #TODO: remove cost???
		self.start = start
		self.resources_req = resources_req
		self.resources = resources
		if capacity_req is not None :
			self.capacity_req = capacity_req
		else :
			self.capacity_req = self.length

	def resources_req_list(self) :
		return [ R for RA in self for R in RA ]

	def __getitem__(self,index) :
		if isinstance(index,int) :
			return self.resources_req[index]
		elif isinstance(index,Resource) :
			max_req = max([ RA[index] for RA in self.resources_req if index in RA ] + \
                                      [ int(index in self.resources_req) ] ) #if contained a simple resource
			return max_req
		else :
			raise Exception('ERROR: tasks can only take integers and resources as index, not '+str(index))
		return self

	def __iter__(self) :
		if self.resources_req is None :
			raise Exception('ERROR: task '+str(self)+' does not have any resource requirements')
		return self.resources_req.__iter__()
		
	def __len__(self) :
		return self.length

	def __iadd__(self,other) :
		if _isiterable(other) :
			for x in other : self += x		
		elif isinstance(other,(Resource,_ResourceAffine)) :
			if self.resources_req is None :
				self.resources_req = list()
			self.resources_req.append(other)
		else :
			raise Exception('ERROR: cant add '+str(other)+' to task '+str(self))
		return self

	def __lt__(self,other) :
		if isinstance(other,Resource) :
			return Precedence(left=self,right=other,kind='first')
		return _TaskAffine(self) < other

	def __gt__(self,other) :
		if isinstance(other,Resource) :
			return Precedence(left=self,right=other,kind='last')
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



class _TaskAffine(_SchedElementAffine) :

	def __init__(self,unknown=None) :
		_SchedElementAffine.__init__(self,unknown=unknown,element_class=_SchedElement)

	def __lt__(self,other) :
		if _isiterable(other) :
			return [ self < x for x in other ]
		if not isinstance(other,type(self)) :
			return self < _TaskAffine(other)
		return _TaskAffineConstraint(self-other,'<')

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
		return _TaskAffineConstraint(self-other,'<=')

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
		return _TaskAffineConstraint(self-other,'<<')

	def __rshift__(self,other) :
		if _isiterable(other) :
			return [ self >> x for x in other ]
		if not isinstance(other,type(self)) :
			return self >> _TaskAffine(other)
		return _TaskAffine(other) << self



class _TaskAffineConstraint(_TaskAffine) :
	"""
	A representation of some inequality of e.g. the form T1 + T2*3 + 2 < 0
	The inquality sign is determined by parameter comp_operator. 
	"""
	def __init__(self,task_affine,comp_operator) :
		_TaskAffine.__init__(self)
		self.update(_DICT_TYPE(task_affine))
		self.comp_operator = comp_operator

	def __repr__(self) :
		s = self.__repr__()
		s += ' ' + str(sign) + ' 0'



class _Constraint(_SchedElement) :
	"""
	An arbitrary constraint
	"""
	def __init__(self) :
		_SchedElement.__init__(self,name='',numeric_name_prefix='C')



class Precedence(_Constraint) :
	"""
	A precedence constraint of two tasks, left and right, and an offset.
	right might also be a number. The kinds of precedenceds are:

	lax :  e.g. T1 + 3 < T2
	tight : e.g. T1 + 3 <= T2
	cond : e.g. T1 + 3 << T2
	low : e.g. T1 > 3
	up : e.g. T1 < 3
	"""
	def __init__(self,left,right,offset=0,kind='lax') :
		_Constraint.__init__(self)
		self.left = left
		self.right = right
		self.offset = offset
		self.kind = kind

	def tasks(self) :
		return [self.left,self.right]

	def __repr__(self) :
		kind_to_comp_operator = { 'lax':'<', 'tight':'<=', 'cond':'<<', 'low':'>', 'up':'<', 'first':'<', 'last':'>' }
		s = str(self.left) + ' '
		if self.offset != 0 :
			s += '+ ' + str(self.offset) + ' '
		s += str(kind_to_comp_operator[self.kind]) + ' ' + str(self.right)
		return s

	def __str__(self) :
		return self.__repr__()

	def __hash__(self) :
		return self.__repr__().__hash__()
		


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
		elif isinstance(other,Precedence) :
			# check if each task in prec requires resource
			wrong_tasks = [ T for T in other.tasks() if not self in T.resources_req_list()]
			if not wrong_tasks :
				self.precs.add(other)
			else :
				raise Exception('ERROR: Precedence '+str(other)+' includes task(s) '+\
                                                 ','.join([str(T) for T in wrong_tasks])+\
                                                 ' that do(es) not require resource '+str(self))
		elif _isiterable(other) :
			for x in other : self += x	
		else :
			raise Exception('ERROR: cant add '+str(other)+' to resource '+str(self))
		return self

	def __mul__(self,other) :
		return _ResourceAffine(self) * other

	def __or__(self,other) :
		return _ResourceAffine(self) | other
	
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

	

class _ResourceAffine(_SchedElementAffine) :

	def __init__(self,unknown=None) :
		_SchedElementAffine.__init__(self,unknown=unknown,element_class=Resource,affine_operator='|')

	def __or__(self,other) :
		return super(_ResourceAffine,self).__add__(_ResourceAffine(other)) #add of superclass



		
			
			
		
		


















