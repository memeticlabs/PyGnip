#!/usr/bin/env python

import urllib2
import base64
import json
import sys


class GnipBasicAuth():

    """Gnip Basic Authentication handler"""


    def __init__(self, username, password, account_name):
        if type(username) == unicode:
            username = bytes(username)
        if type(password) == unicode:
            password = bytes(username)

        self.auth_handler = 'Basic ' + \
            base64.urlsafe_b64encode("%s:%s" % (username, password))

        self.account = account_name