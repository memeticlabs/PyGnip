#!/usr/bin/env python
import urllib2
import base64
import json
import sys
from pygnip.binder import bind_api

class RuleAPI(object):
	"""Gnip Rules API"""

	def __init__(self, auth,
              host='https://api.gnip.com:443',
              account=None,
              publishers="twitter",
              streams="track",
              secure=True):

		self.auth = auth.auth_handler
		self.host = host
		self.account = account or auth.account
		self.streams = streams
		self.publishers = publishers
		self.url = '%s/accounts/%s/publishers/%s/streams/%s/prod/rules.json' \
        			% (self.host, self.account, self.publishers, self.streams)

	def add_rule(self, rule):
		"""add a tracking rule.
		format:
		kwargs = {
			"tag" : "airwoot_test_1",
			"value" : "(airwoot or woot)"
		}

		on success, response code = 201
		"""
		response = None
		kwargs ={"rules": [rule]}

		try:
			request = urllib2.Request(url=self.url, data=json.dumps(kwargs))
			request.add_header('Authorization', self.auth)
			request.add_header('Content-type', 'application/json')
			response = urllib2.urlopen(request)
		except urllib2.HTTPError as e:
			print e.read()

		if response.code == 201:
			return True
		else:
			print "Rule %s could not be added. Request failed with response \
					code %s" % (rule['tag'], response.code)
			return False

	def get_rules(self):
		"""fetch all rules and display"""
		response = None

		try:
			request = urllib2.Request(url=self.url)
			request.add_header('Authorization', self.auth)
			request.add_header('Content-type', 'application/json')
			response = urllib2.urlopen(request)
		except urllib2.HTTPError as e:
			print e.read()

		if response.code == 200:
			return response.read()
		else:
			print "Rule could not be fetched. Request failed with response \
					code %s" % (response.code)
			return None		


	
