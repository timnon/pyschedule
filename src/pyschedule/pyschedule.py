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
python package to formulate and solve resource-constrained
scheduling problems
"""

#TODO: time in str and datetime
#TODO: add global unit
#TODO: set start like T.start = 4 which will use this as a constraint

import sys, hashlib
from collections import OrderedDict


try: # allow Python 2 vs 3 compatibility
	maketrans = str.maketrans
except AttributeError:
	from string import maketrans

def OR(L) :
	return reduce(lambda x, y : x | y, L)

def AND(L) :
	return reduce(lambda x, y : x & y, L)

def isnumeric(var) :
	return isinstance(var,(int,float))

def isiterable(var) :
	return isinstance(var,(list,set,tuple)) #restriction to list,set,tuple to avoid funny cases



class SchedElement(object) :

	def __init__(self,name) :
		# purely numeric names are not allowed
		if isnumeric(name) :
			name = 'E'+str(name)
		# remove illegal characters
		trans = maketrans("-+[] ->/","________")
		self.name = str(name).translate(trans)

	def __str__(self) :
		return self.name
	
	def __repr__(self) :
		return self.__str__()

	def __hash__(self) :
		return self.__repr__().__hash__()



class SchedElementAffine(OrderedDict) :

	def __init__(self,unknown=None,element_class=None) :
		OrderedDict.__init__(self)
		self.element_class = element_class
		if unknown == None :
			pass
		elif isinstance(unknown,self.element_class) :
			self[unknown] = 1
		elif isnumeric(unknown) :
			self[1] = unknown
		elif isinstance(unknown,type(self)) :
			self.update(unknown)
		else :
			raise Exception('ERROR: cant init '+str(self)+' from '+str(unknown))

	def __add__(self,other) :
		if isiterable(other) :
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
		if isiterable(other) :
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
		return '+'.join([ format_coeff(self[key])+str(key) for key in self ])

	def __hash__(self) :
		return self.__repr__().__hash__()


	
class Scenario(SchedElement):
	
	def __init__(self,name='scenario not named') :
		SchedElement.__init__(self,name)
		self.tasks = set()
		self.resources = set()
		self.precs = set()
		self.objective = TaskAffine()

	def Task(self,name,length=1) :
		T = Task(name,length)
		self.tasks.add(T)
		return T

	def Resource(self,name,capacity=None) :
		R = Resource(name,capacity)
		self.resources.add(R)
		return R

	def __iadd__(self,other) :
		if isiterable(other) :
			for x in other : self += x
		elif isinstance(other,Precedence) :
			self.precs.add(other)
		elif isinstance(other,(Task,TaskAffine)) : #TODO: attention Precedence is also TaskAffine
			self.objective += other
		else :
			raise Exception('ERROR: cant add '+str(other)+' to scenario '+str(self))
		return self
			
	def solution(self) :
		solution = [ (str(T),str(R),T.start,T.start+T.length) \
                             for T in self.tasks for R in T.actual_resources ]
		solution += [ (str(T),'',T.start,T.start+T.length) \
                             for T in self.tasks if not T.resource_req.resources() ]
		solution = sorted(solution, key = lambda x : (x[1],x[2])) # sort according to resource and start
		return solution

	def __repr__(self) :
		s = '\n##############################################\n'
		s += 'SCENARIO: '+str(self)+'\n\n'
		#print objective
		s += 'OBJECTIVE: '+str(self.objective)+'\n\n'
		# print tasks
		s += 'TASKS WITH RESOURCES:\n'
		s += '\n'.join([ str(T)+' : '+ str(T.resource_req) for T in sorted(self.tasks) ]) + '\n\n'
		# print resources
		s += 'RESOURCES WITH PRECEDENCES:\n'
		for R in self.resources :
			s += str(R)+' : '+ ','.join([ P.__repr__() for P in R.precs ]) + '\n'
		s += '\n'
		# print precedences
		s += 'GLOBAL PRECEDENCES:\n'
		s += '\n'.join([ str(P) + ' : ' + P.__repr__() for P in self.precs ]) + '\n'
		s += '##############################################\n'
		return s



class Task(SchedElement) :

	def __init__(self,name,length=1,start=None) :
		SchedElement.__init__(self,name)
		self.start = start
		self.length = length
		self.resource_req = ResourceReq()

	def __len__(self) :
		return self.length

	def __iadd__(self,other) :
		if isinstance(other,(Resource,ResourceAffine,ResourceReq)) :
			self.resource_req += ResourceReq(other)
		elif isiterable(other) :
			for x in other : self += x
		else :
			raise Exception('ERROR: cant add '+str(other)+' to task '+str(self))
		return self

	def __lt__(self,other) :
		return TaskAffine(self) < other

	def __gt__(self,other) :
		return TaskAffine(self) > other

	def __le__(self,other) :
		return TaskAffine(self) <= other

	def __ge__(self,other) :
		return TaskAffine(self) <= other

	def __ne__(self,other) :
		return TaskAffine(self) != other

	def __lshift__(self,other) :
		return TaskAffine(self) << other

	def __rshift__(self,other) :
		return TaskAffine(self) >> other

	def __add__(self,other) :
		return TaskAffine(self) + other

	def __sub__(self,other) :
		return TaskAffine(self) - other

	def __mul__(self,other) :
		return TaskAffine(self) * other

	#TODO: cant overload ==-operator, seems to screw up sets



class TaskAffine(SchedElementAffine) :

	def __init__(self,unknown=None) :
		SchedElementAffine.__init__(self,unknown=unknown,element_class=Task)

	def __lt__(self,other) :
		if isiterable(other) :
			return [ self < x for x in other ]
		if not isinstance(other,type(self)) :
			return self < TaskAffine(other)
		return Precedence(TaskAffine(self),'<',TaskAffine(other))

	def __gt__(self,other) :
		if isiterable(other) :
			return [ self > x for x in other ]
		if not isinstance(other,type(self)) :
			return self > TaskAffine(other)
		return Precedence(TaskAffine(self),'>',TaskAffine(other))

	def __le__(self,other) :
		if isiterable(other) :
			return [ self <= x for x in other ]
		if not isinstance(other,type(self)) :
			return self <= TaskAffine(other)
		return Precedence(TaskAffine(self),'<=',TaskAffine(other))

	def __ge__(self,other) :
		if isiterable(other) :
			return [ self >= x for x in other ]
		if not isinstance(other,type(self)) :
			return self >= TaskAffine(other)
		return Precedence(TaskAffine(self),'>=',TaskAffine(other))

	def __ne__(self,other) :
		if isiterable(other) :
			return [ self != x for x in other ]
		if not isinstance(other,type(self)) :
			return self != TaskAffine(other)
		return Precedence(TaskAffine(self),'!=',TaskAffine(other))

	def __lshift__(self,other) :
		if isiterable(other) :
			return [ self << x for x in other ]
		if not isinstance(other,type(self)) :
			return self << TaskAffine(other)
		return Precedence(TaskAffine(self),'<<',TaskAffine(other))

	def __rshift__(self,other) :
		if isiterable(other) :
			return [ self >> x for x in other ]
		if not isinstance(other,type(self)) :
			return self >> TaskAffine(other)
		return Precedence(TaskAffine(self),'>>',TaskAffine(other))



class Precedence(TaskAffine) :

	def __init__(self,left,kind,right) :
		TaskAffine.__init__(self)
		#SchedElement.__init__(self,None)
		if not isinstance(left,TaskAffine) :
			left = TaskAffine(left)
		if not isinstance(right,TaskAffine) :
			right = TaskAffine(right)
		if not kind in {'<','>','<<','>>','<=','>=','!='} :
			raise Exception('ERROR: '+str(kind)+' does not describe a precedence')
		if kind == '>>' or kind == '>' :
			left, right = right, left
			if kind == '>>' : kind = '<<'
			if kind == '>' : kind = '<'
			if kind == '>=' : kind = '<='
		self.left  = left
		self.right = right
		self.kind = kind
		self.update(self.left - self.right) # main precedence <= 0
		#TODO: add many more checkers for precedences
		nr_tasks = len([ key for key in self if isinstance(key,Task) ])
		if nr_tasks > 2 :
			raise Exception('ERROR: too many tasks in precedence ' + str(self))

	def tasks(self) :
		return set([ T for T in self if isinstance(T,Task) ])

	def __repr__(self) :
		return str(self.left) + str(self.kind) + str(self.right)

	def __hash__(self) :
		return self.__repr__().__hash__()



class Resource(SchedElement) :

	def __init__(self,name=None,capacity=None) :
		SchedElement.__init__(self,name)
		self.capacity = capacity
		self.precs = set()

	def __iadd__(self,other) :
		if isinstance(other,Task) :
			other += self
			return self
		elif isinstance(other,Precedence) :
			# check if each task in prec requires resource
			wrong_tasks = [ T for T in other.tasks() if not self in T.resource_req.resources()]
			if not wrong_tasks :
				self.precs.add(other)
			else :
				raise Exception('ERROR: Precedence '+str(other)+' includes task(s) '+\
                                                 ','.join([str(T) for T in wrong_tasks])+\
                                                 ' that do(es) not require resource '+str(self))
		elif isiterable(other) :
			for x in other : self += x	
		else :
			raise Exception('ERROR: cant add '+str(other)+' to resource '+str(self))
		return self
		
	def __sub__(self,other) :
		return ResourceAffine(self) - other

	def __add__(self,other) :
		return ResourceAffine(self) + other

	def __mul__(self,other) :
		return ResourceAffine(self) * other

	def __or__(self,other) :
		return ResourceAffine(self) | other



class ResourceAffine(SchedElementAffine) :

	def __init__(self,unknown=None) :
		SchedElementAffine.__init__(self,unknown=unknown,element_class=Resource)

	def __or__(self,other) :
		if isiterable(other) :
			return [ self | x for x in other ]
		if not isinstance(other,type(self)) :
			return self | ResourceAffine(other)
		req = ResourceReq()
		req.add(self)
		req.add(other)
		return req



class ResourceReq(set) :

	def __init__(self,unknown=None) :
		set.__init__(self)
		if unknown == None :
			pass
		elif isinstance(unknown,Resource) :
			self.add(ResourceAffine(unknown))
		elif isinstance(unknown,ResourceAffine) :
			self.add(unknown)
		elif isinstance(unknown,ResourceReq) :
			self.clear()
			self.update(unknown)
		else :
			raise Exception('ERROR: cant init resource requirement from '+str(unknown))

	def resources(self) :
		return [ R for RA in self for R in RA ]

	def __add__(self,other) :
		if len(self) :
			old = set(self)
			self.clear()
			self.update([ RA + RA_ for RA_ in old for RA in ResourceReq(other) ])
		else :
			self.update(ResourceReq(other))
		return self

	def __or__(self,other) :
		self.add(ResourceReq(other))
		return self

	def __repr__(self) :
		return ' | '.join([ str(RA) for RA in self ])















