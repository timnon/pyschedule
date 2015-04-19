#! /usr/bin/env python
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

#TODO: cpoptimier with cond precedence constraints


from collections import OrderedDict as _DICT_TYPE

try: # allow Python 2 vs 3 compatibility
	_maketrans = str.maketrans
except AttributeError:
	from string import maketrans as _maketrans

def OR(L) :
	"""
	method to iterate the or-operator over a list to allow lists of alternative resources, e.g. OR([R1,R2,R3]) = R1 | R2 | R3
	"""
	return reduce(lambda x, y : x | y, L)

def _isnumeric(var) :
	return isinstance(var,(int)) # only integers are accepted

def _isiterable(var) :
	return isinstance(var,(list,set,tuple)) #restriction to list,set,tuple to avoid funny cases



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

	def __init__(self,unknown=None,element_class=None,kind='+') :
		_DICT_TYPE.__init__(self)
		self.element_class = element_class
		self.kind = kind

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

	def __repr__(self) :
		def format_coeff(val) :
			if val != 1 :
				return str(val)+'x'
			else :
				return ''
		return (' '+self.kind+' ').join([ format_coeff(self[key])+str(key) for key in self ])

	def __hash__(self) :
		return self.__repr__().__hash__()


	
class Scenario(_SchedElement):
	
	def __init__(self,name='scenario not named') :
		_SchedElement.__init__(self,name,numeric_name_prefix='S')
		self.objective = _TaskAffine()
		self.T = _DICT_TYPE() #tasks
		self.R = _DICT_TYPE() #resources
		self.precs = list()

	def Task(self,name,length=1) :
		"""
		Adds a task with the given name to the scenario. Task names need to be unique.
		"""
		T = Task(name,length)
		if str(T) not in self.T : #[ str(T_) for T_ in self.tasks ] :
			self.T[str(T)] = T
		else :
			raise Exception('ERROR: task with name '+str(T)+' already contained in scenario '+str(self))
		return T

	def tasks(self) :
		return self.T.values()

	def Resource(self,name,capacity=None) :
		"""
		Adds a resource with the given name to the scenario. Resource names need to be unique.
		"""
		R = Resource(name,capacity)
		if str(R) not in self.R : #[ str(R_) for R_ in self.resources ] :
			self.R[str(R)] = R #.append(R)
		else :
			raise Exception('ERROR: resource with name '+str(R)+' already contained in scenario '+str(self))
		return R

	def resources(self) :
		return self.R.values()

	def R(self,name) :
		return self._resources[name]

	def solution(self) :
		"""
		Returns the last computed solution in tabular form with columns: task, resource, start, end
		"""
		solution = [ (str(T),str(R),T.start,T.start+T.length) \
                             for T in self.tasks() for R in T.resources ]
		solution += [ (str(T),'',T.start,T.start+T.length) \
                             for T in self.tasks() if not T.resources_req.resources() ]
		solution = sorted(solution, key = lambda x : (x[1],x[2])) # sort according to resource and start
		return solution

	def use_makespan_objective(self) :
		"""
		Set the objective to the makespan of all included tasks without a fixed start
		"""
		self.objective.clear()
		tasks = list(self.tasks())
		makespan = self.Task('MakeSpan')
		makespan += self.Resource('MakeSpan')
		self += makespan*1
		for T in tasks :
			if not T.start :
				self += T < makespan

	def clear_task_starts(self) :
		"""
		Remove the start times of all tasks
		"""
		for T in self.tasks() :
			T.start = None

	def precs_lax(self) :
		return [ prec for prec in self.precs
                         if isinstance(prec.left,Task) and isinstance(prec.right,Task) 
                         and prec.kind == '<' and _isnumeric(prec.offset) ]

	def precs_tight(self) :
		return [ prec for prec in self.precs
                         if isinstance(prec.left,Task) and isinstance(prec.right,Task) 
                         and prec.kind == '<=' and _isnumeric(prec.offset) ]

	def precs_cond(self) :
		return [ prec for prec in self.precs
                         if isinstance(prec.left,Task) and isinstance(prec.right,Task) 
                         and prec.kind == '<<' and _isnumeric(prec.offset) ]

	def precs_low(self) :
		return [ prec for prec in self.precs
                         if _isnumeric(prec.left) and isinstance(prec.right,Task)
                         and prec.kind == '<' and prec.offset == 0 ]

	def precs_up(self) :
		return [ prec for prec in self.precs
                         if isinstance(prec.left,Task) and _isnumeric(prec.right)
                         and prec.kind == '<' and prec.offset == 0 ]

	def __iadd__(self,other) :
		if _isiterable(other) :
			for x in other : self += x
			return self

		elif isinstance(other,_TaskConstraint) :
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
				if other.kind == '<' :
					self.precs.append(Precedence(left=left,offset=offset,kind='<',right=right))
				elif other.kind == '<=' :
					self.precs.append(Precedence(left=left,offset=offset,kind='<=',right=right))
				elif other.kind == '<<' :
					shared_resources = list( set(left.resources_req.resources()) & set(right.resources_req.resources()) )
					prec = Precedence(left=left,offset=offset,kind='<<',right=right)
					if not shared_resources :
						raise Exception('ERROR: tried to add precedence '+str(prec)+' but tasks dont compete for resources')
					self.precs.append(prec)
				return self
			elif pos_tasks and not neg_tasks :
				left = pos_tasks[0]
				right = -offset
				self.precs.append(Precedence(left=left,kind='<',right=right))
				return self
			elif not pos_tasks and neg_tasks :
				left = offset
				right = neg_tasks[0]
				self.precs.append(Precedence(left=left,kind='<',right=right))
				return self

			raise Exception('ERROR: cannot add task constraint '+str(other)+' to scenario')

		elif isinstance(other,(Task,_TaskAffine)) : #TODO: attention Precedence is also _TaskAffine
			self.objective += other
			return self

		raise Exception('ERROR: cant add '+str(other)+' to scenario '+str(self))

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
		s += '\n'.join([ str(T)+' : '+ str(T.resources_req) for T in sorted(self.tasks()) ]) + '\n\n'
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
			s += '\n'.join([ P.__repr__() for P in self.bounds_low() ]) + '\n'
			s += '\n'

		if self.precs_up() :
			# print precedences
			s += 'UPPER BOUNDS:\n'
			s += '\n'.join([ P.__repr__() for P in self.bounds_up() ]) + '\n'
			s += '\n'

		s += '##############################################\n'
		return s



class Task(_SchedElement) :
	"""
	A task to be processed by at least one resource
	"""

	def __init__(self,name,length=1,start=None,resources=None) :
		_SchedElement.__init__(self,name,numeric_name_prefix='T')
		self.start = start
		self.length = length
		self.resources = resources
		self.resources_req = _ResourceReq()

	def __len__(self) :
		return self.length

	def __iadd__(self,other) :
		if _isiterable(other) :
			for x in other : self += x		
		elif isinstance(other,(Resource,_ResourceAffine,_ResourceReq)) :
			self.resources_req += other
		else :
			raise Exception('ERROR: cant add '+str(other)+' to task '+str(self))
		return self

	def __lt__(self,other) :
		return _TaskAffine(self) < other

	def __gt__(self,other) :
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



class _TaskAffine(_SchedElementAffine) :

	def __init__(self,unknown=None) :
		_SchedElementAffine.__init__(self,unknown=unknown,element_class=Task)

	def __lt__(self,other) :
		if _isiterable(other) :
			return [ self < x for x in other ]
		if not isinstance(other,type(self)) :
			return self < _TaskAffine(other)
		return _TaskConstraint(self-other,'<')

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
		return _TaskConstraint(self-other,'<=')

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
		return _TaskConstraint(self-other,'<<')

	def __rshift__(self,other) :
		if _isiterable(other) :
			return [ self >> x for x in other ]
		if not isinstance(other,type(self)) :
			return self >> _TaskAffine(other)
		return _TaskAffine(other) << self



class _TaskConstraint(_TaskAffine) :

	def __init__(self,task_affine,kind) :
		_TaskAffine.__init__(self)
		self.update(_DICT_TYPE(task_affine))
		self.kind = kind



class Precedence(object) :
	"""
	A precedence of the form T1+5<=T2 for left=T1, offset=5, kind='<=', and right=T2
	or 8<T1 for left=8, offset=0, kind='<', and right=T1. The typing should be clear
	from the context, e.g. precedences of the former type should be always a separate list
	than precedences of the latter type. This makes sense since different precedences
	are treated somewhat differenctly in any solver.

	Precedences should not be directly generated by via operators like <, << or <=
	"""
	
	def __init__(self,left=0,offset=0,kind='<',right=0) :
		self.left = left
		self.offset = offset
		self.kind = kind
		self.right = right

	def tasks(self) :
		return [self.left,self.right]

	def __repr__(self) :
		s = str(self.left) + ' '
		if self.offset != 0 :
			s += '+ ' + str(self.offset) + ' '
		s += str(self.kind) + ' ' + str(self.right)
		return s

	def __hash__(self) :
		return self.__repr__().__hash__()



class Resource(_SchedElement) :
	"""
	A resource which can process at most one task per time step
	"""

	def __init__(self,name=None,capacity=None) :
		_SchedElement.__init__(self,name,numeric_name_prefix='R')
		self.capacity = capacity

	def __iadd__(self,other) :
		if isinstance(other,Task) :
			other += self
			return self
		elif isinstance(other,Precedence) :
			# check if each task in prec requires resource
			wrong_tasks = [ T for T in other.tasks() if not self in T.resources_req.resources()]
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
		

	def __add__(self,other) :
		return _ResourceReq(_ResourceAffine(self)) + other

	def __mul__(self,other) :
		return _ResourceAffine(self) * other

	def __or__(self,other) :
		return _ResourceAffine(self) | other



class _ResourceAffine(_SchedElementAffine) :

	def __init__(self,unknown=None) :
		_SchedElementAffine.__init__(self,unknown=unknown,element_class=Resource,kind='|')

	def __or__(self,other) :
		return super(_ResourceAffine,self).__add__(_ResourceAffine(other)) #add of superclass

	def __add__(self,other) :
		return _ResourceReq(self) + other



class _ResourceReq(list) :

	def __init__(self,unknown=None) :
		list.__init__(self)
		if unknown :
			self.append(_ResourceAffine(unknown))

	def __add__(self,other) :
		if _isiterable(other) :
			for x in other : self += x
		other = _ResourceAffine(other)
		if set(other) & set(self.resources()) :
			raise Exception('ERROR: '+str(other)+' already somewhat contained in resource requirement '+str(self))
		self.append(other)
		return self

	def __iadd__(self,other) :
		self = self + other
		return self

	def __repr__(self) :
		return ' + '.join([ str(x) for x in self])

	def resources(self) :
		return [ R for RA in self for R in RA ]

	def capacity(self,R) :
		RA = [ RA_ for RA_ in self if R in RA_ ][0]
		return RA[R]
			

















