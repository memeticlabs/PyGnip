#!/usr/bin/env python
import gzip
import json
import base64
import urllib2
from StringIO import StringIO
from pymongo.errors import DuplicateKeyError
from config import MainConfig as settings
from pygnip.connection_pool import mongodbapi as dbapi


class RequestWithMethod(urllib2.Request):

    def __init__(self, url, method, data, headers={}):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class HistoricalAPI(object):

    """Gnip's historical api
    Historical Jobs consist of three distinct phases:

    `Phase 1`: The customer creates a new job, and an estimate is run for that returns the expected volumes and time required.

    API Methods:

    * create_job()

    `Phase 2`: The customer either accepts or rejects the job based on the values returned in the estimate.

    API Methods:

    * accept()
    * reject()

    `Phase 3`: If the customer accepted the job, the data is collected into files, which are then made available for download by the customer.

    API Methods:

    * ready()
    * download()

    """

    def __init__(self, auth, jobid=None):
        self.auth = auth.auth_handler
        self.account = auth.account
        self.request_url = "https://historical.gnip.com/accounts/%s/jobs.json" % self.account
        self.job_id = jobid

    @property
    def job_url(self):
        if self.job_id is not None:
            return "https://historical.gnip.com:443/accounts/%s/publishers/twitter/historical/track/jobs/%s.json" % (self.account, self.job_id)

    @property
    def result_url(self):
        if self.job_id is not None:
            return "https://historical.gnip.com:443/accounts/%s/publishers/twitter/historical/track/jobs/%s/results.json" % (self.account, self.job_id)

    def create_job(self,
                   fromDate,
                   toDate,
                   rules,
                   publisher="twitter",
                   streamType="track",
                   dataFormat="original",
                   title="Default Job",
                   serviceUsername=None):
        """create a job with the given rule"""
        if not (fromDate and toDate):
            return None

        serviceUsername = self.account

        response = None
        job_id = None
        kwargs = {
            "publisher": publisher,
            "streamType": streamType,
            "dataFormat": dataFormat,
            "fromDate": fromDate,
            "toDate": toDate,
            "title": title,
            "serviceUsername": serviceUsername,
            "rules": rules
        }
        # return json.dumps(kwargs)

        try:
            request = urllib2.Request(
                url=self.request_url, data=json.dumps(kwargs))
            request.add_header('Authorization', self.auth)
            request.add_header('Content-type', 'application/json')
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print e.read()

        if response.code == 201:
            response = json.loads(response.read())
            self.job_url = response['jobURL']
            try:
                job_id = response['jobURL'].split('/')[-1].split('.json')[0]
            except Exception as e:
                print e
                return response

        return job_id

    def reject(self):
        """Reject a job"""
        kwargs = {
            "status": "reject"
        }
        response = None
        try:
            request = RequestWithMethod(
                url=self.job_url, method='PUT', data=json.dumps(kwargs))
            request.add_header('Authorization', self.auth)
            request.add_header('Content-type', 'application/json')
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print e.read()

        if response.code == 200:
            if json.loads(response.read())['status'] == "rejected":
                print "Job id: %s succesfully rejected"
                return True
        else:
            return False

    def accept(self):
        """Accept a job"""
        kwargs = {
            "status": "accept"
        }
        response = None
        try:
            request = RequestWithMethod(
                url=self.job_url, method='PUT', data=json.dumps(kwargs))
            request.add_header('Authorization', self.auth)
            request.add_header('Content-type', 'application/json')
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print e.read()

        if response.code == 200:
            if json.loads(response.read())['status'] == "accepted":
                print "Job id: %s succesfully accepted"
                return True
        else:
            return False

    def review(self):
    	"""Review the created job in order to accept or reject
    	on the basis of estimation quote"""

    	# TODO: we should also be able to see the rule which was
    	# assoicated with the job. Gnip result do not show the rule
    	# if there is no way to get it from Gnip then we might have
    	# to store this info in our db.

    	response = None
    	try:
            request = urllib2.Request(url=self.job_url)
            request.add_header('Authorization', self.auth)
            request.add_header('Content-type', 'application/json')
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print e.read()

        if response.code == 200:
         	return json.loads(response.read())

    def ready(self):
    	"""Monitor the status of accepted job"""
        response = None
    	try:
            request = urllib2.Request(url=self.job_url)
            request.add_header('Authorization', self.auth)
            request.add_header('Content-type', 'application/json')
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print e.read()

        if response.code == 200:
         	response = json.loads(response.read())
         	if not response['status'] == "delivered":
         		return False, response['percentComplete']
         	else:
         		return True, response['percentComplete']

    def download_urls(self):
    	"""Download all the S3 data urls from result url"""
    	# download all urls
    	response = None
    	try:
            request = urllib2.Request(url=self.result_url)
            request.add_header('Authorization', self.auth)
            request.add_header('Content-type', 'application/json')
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print e.read()

        if response.code == 200:
         	response = json.loads(response.read())
         	print "total urls to download:%s" % response['urlCount']
         	return response['urlList']

    def fetch_data_from_url(self, url):
    	"""fetch the data from s3 url.

    	Gnip stores json in gzipped format which consists of
    	unnecessary carriage returns and meta information about
    	fetched acitvities.

    	this method cleans up everything returns an array of 
    	activities (tweets)
    	"""
    	activities = []
    	data = None
    	try:
    		request = urllib2.Request(url=url)
    		request.add_header('Accept-encoding', 'gzip')
    		response = urllib2.urlopen(request)
    		str_buffer = StringIO(response.read())
    		data = gzip.GzipFile(fileobj=str_buffer)
    		data = data.read()

    	except Exception as e:
    		print e
    		pass

		    # split all activities \r\n
        data = data.split('\r\n')

        # clean up, populate activity array
        for activity in data:
            try:
                activity = json.loads(activity)
                # check if it is tweet
                if 'id' in activity.keys():
                    activity['_id'] = activity['id_str']
                    activities.append(activity)
            except:
                pass

        return activities

    def dump_to_db(self, db="mongo", coll="mentions"):
    	"""Download the Completed Job"""
    	self.db = None
    	if db == "mongo":
    		self.db = dbapi(dbapi.MONGO_DB, coll)

    	# in case of redis, set the key pattern
    	if self.db is None:
    		return

    	# retrieve the data url list
    	urllist = self.download_urls()

    	# measure db count
    	db_size = self.db.count()
    	# start batch fetching of the data
    	for each_url in urllist:
    	    activities = self.fetch_data_from_url(each_url)
            print "fetched %s" % len(activities)
            try:
                status = self.db.insert(activities, continue_on_error=True)
            except DuplicateKeyError:
                pass


		# measure and update db count
        updated_db_size = self.db.count()
        print "%s total documents added" % (int(updated_db_size) - int(db_size))



