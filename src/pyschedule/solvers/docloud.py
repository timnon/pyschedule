#!/usr/bin/python
# coding: utf-8

# # Solving Optimization Problems On The Cloud With Python
# 
# ## Author: [Jean-Francois Puget](https://www.ibm.com/developerworks/community/blogs/jfp/?lang=en)
# 
# We present a simple Python client for solving problems on DOcloud.  Additional explanations are 
# available in my [blog entry](https://www.ibm.com/developerworks/community/blogs/jfp/entry/using_cplex_on_docloud_with_python?lang=en)
# 
# In order to use it you need a valid subscription to DOcloud. Instructions to get a key are available on 
# the DOcloud page. Look for the developer drop down menu. If you are logged in with an existing IBM id, then you should select the Get API & Base URL item. If you are not logged in then you should go to the developer community, and register for the free trial.
# 
# Once you have completed the onboarding step you must paste your key and the base url in the code below.



# We will use a single class that is initialized with the above credentials, then can be used to launch jobs with a single call.

import json, requests, os, time, sys

class DOcloud:
    """ Client for DOcloud """
    
    def __init__(self, base_url, api_key, **kwargs):
        self.url = base_url+'jobs'
        self.auth = {'X-IBM-Client-ID' : api_key}
        self.headers_post = {'X-IBM-Client-ID' : api_key, 'Content-Type' : 'application/json'}
        self.headers_put = {'X-IBM-Client-ID' : api_key, 'Content-Type' : 'application/octet-stream'}
        self.verbose = kwargs['verbose'] if 'verbose' in kwargs else False
        requests.delete(self.url, headers=self.auth)
        
    def execute(self, filenames):
        mydata = {}
        for filename in filenames:
                filename_short = os.path.basename(filename)
                with open(filename) as f:
                    mydata[filename_short] = f.read()                                            
        attachments = {'attachments' : mydata.keys()}
        r = requests.post(self.url, headers=self.headers_post, data=json.dumps(attachments))
        if r.status_code != 201: print 'unsuccessful job creation %s' % r.status_code
        job = r.headers['location']

        for filename in mydata:
            r = requests.put(job + '/attachments/'+filename+'/blob', headers=self.headers_put, data=mydata[filename])
            if r.status_code != 204: print '%s upload failed %d' % (filename, r.status_code)
            elif self.verbose: print '%s upload succeeded' % filename
        r = requests.post(job+'/execute', headers=self.auth)
        if r.status_code != 204: print 'execute failed to start %d' % r.status_code
        elif self.verbose: print ' '.join(mydata.keys())+' execute started succesfully' 
        return job
    
    def get_info(self, job):
        r = requests.get(job, headers=self.headers_post)
        if r.status_code != 200: print 'cannot get info %s' % r.status_code
        return json.loads(r.content)
    
    def get_log(self, job):
        r = requests.get(job+'/log/blob', headers=self.headers_post)
        if r.status_code != 200: print 'cannot get info %s' % r.status_code
        elif self.verbose: print 'log downloaded succesfully'
        return r.content

    def get_result(self, job):
        status = 'RUNNING'
        job_info = {}
        while status != 'PROCESSED' and status != 'FAILED':
            time.sleep(1)
            job_info = self.get_info(job)
            status = job_info['executionStatus']
            if self.verbose: print status
        if status == 'FAILED':
            print 'Job failed : '
            print job_info['failure']
            return {}
        else:
            r = requests.get(job+'/attachments/solution.json/blob', headers=self.headers_post)
            if r.status_code != 200: print 'result download failed %d' % r.status_code
            elif self.verbose: print 'result downloaded succesfully'

            return json.loads(r.text)
    
    def clean(self, job):
        requests.delete(job, headers=self.auth)
        
    def clean_all(self):
        requests.delete(self.url, headers=self.auth)
        
    def solve(self, filenames):
        job = self.execute(filenames)
        result = self.get_result(job)
	log = self.get_log(job)
        self.clean(job)
	return log

'''
# We can now use the class.  
def main ():

    args = sys.argv[1:]

    if not args:
        print 'usage: [--solution filename][--log logfile] [--verbose] inputfiles '
        sys.exit(1)

    solutionfile = 'solution.json'
    if args[0] == '--solution':
        solutionfile = args[1]
        del args[0:2]

    logfile  = 'log'
    if args[0] == '--log':
        logfile = args[1]
        del args[0:2]
        
    verbose = False
    if args[0] == '--verbose':
        verbose = True
        del args[0:1]
   

    doc = DOcloud(base_url, key, verbose=verbose)

    doc.solve(*args, solution=solutionfile, log=logfile)

if __name__ == '__main__':
  main()
'''
