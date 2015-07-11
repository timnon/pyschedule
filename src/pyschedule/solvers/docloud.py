#!/usr/bin/python
# coding: utf-8
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

import json, requests, os, time, sys

class _DOcloud:
	"""
	Client for DOcloud
	Args:
		base_url:	    base url of DOcloud, get at https://developer.ibm.com/docloud/
		api_key:	     api key, get at https://developer.ibm.com/docloud/
		msg:		 0 means no feedback (default) during computation, 1 means feedback
	"""
    
	def __init__(self, base_url, api_key, msg=0):
		self.url = '%sjobs' % base_url
		self.auth = {'X-IBM-Client-ID' : api_key}
		self.headers_post = {'X-IBM-Client-ID' : api_key, 'Content-Type' : 'application/json'}
		self.headers_put = {'X-IBM-Client-ID' : api_key, 'Content-Type' : 'application/octet-stream'}
		self.msg = msg
		requests.delete(self.url, headers=self.auth)
	
	def execute(self, filenames) :
		# get files and add to attachments
		mydata = {}
		for filename in filenames:
			filename_short = os.path.basename(filename)
			with open(filename) as f:
				mydata[filename_short] = f.read()    

		# create job with file list
		attachments = {'attachments' : list(mydata.keys())}
		r = requests.post(self.url, headers=self.headers_post, data=json.dumps(attachments))
		if r.status_code != 201 :
			print('ERROR: unsuccessful job creation %s' % r.status_code)
		job = r.headers['location']

		# send files
		for filename in mydata :
			r = requests.put('%s/attachments/%s/blob' % (job,filename), 
					 headers=self.headers_put, data=mydata[filename])
			if r.status_code != 204 :
				print('ERROR: %s upload failed %d' % (filename, r.status_code))
			elif self.msg :
					print('INFO: %s upload succeeded' % filename)

		# execute job
		r = requests.post(job+'/execute', headers=self.auth)
		if r.status_code != 204 :
			print('ERROR: execute failed to start %d' % r.status_code)
		elif self.msg :
			print('INFO: cloud execution successfull')
		return job
    
	def get_info(self, job) :
		r = requests.get(job, headers=self.headers_post)
		if r.status_code != 200:
			print('ERROR: cannot get info %s' % r.status_code)
		elif self.msg :
			print('INFO: info downloaded succesfully')
		return json.loads(r.content.decode('utf-8'))
    
	def get_log(self, job) :
		r = requests.get(job+'/log/blob', headers=self.headers_post)
		if r.status_code != 200:
			print('ERROR: cannot get info %s' % r.status_code)
		elif self.msg :
			print('INFO: log downloaded successfully')
		return r.content.decode('utf-8')

	def get_result(self, job) :
		status = 'RUNNING'
		job_info = {}
		# wait until job is finished
		while status != 'PROCESSED' and status != 'FAILED':
			time.sleep(1)
			job_info = self.get_info(job)
			status = job_info['executionStatus']
			if self.msg:
				print('INFO: job status : %s' % status)
		if status == 'FAILED' :
			print('ERROR: job failed : %s' % job_info['failure'])
			return {}
		else:
			r = requests.get('%s/attachments/solution.json/blob' % job, headers=self.headers_post)
			if r.status_code != 200:
				print('ERROR: result download failed %d' % r.status_code)
			elif self.msg :
				print('INFO: result downloaded successfully')
			return json.loads(r.text)
    
	def clean(self, job) :
		requests.delete(job, headers=self.auth)
	
	def solve(self, filenames) :
		""" send files with names in filenames to DOcloud and solve """

		job = self.execute(filenames)
		result = self.get_result(job)
		log = self.get_log(job)
		self.clean(job)
		return log



def solve(base_url,api_key,filenames,msg=0) :
	"""
	solve the model in the given files using DOcloud. Returns the log-file, so write the solution there
	Args:
		base_url:	 base url of DOcloud, get at https://developer.ibm.com/docloud/
		api_key:	 api key, get at https://developer.ibm.com/docloud/
		msg:		 0 means no feedback (default) during computation, 1 means feedback		
	"""
	try :
		import OpenSSL
	except :
		raise Exception('ERROR: pyOpenSSL needs to be installed to use docloud (or python 2.7.9 above). \
                                        Also install ndg-httpsclient and pyasn1')
	doc = _DOcloud(base_url, api_key, msg=msg)
	log = doc.solve(filenames=filenames)
	return log
	






