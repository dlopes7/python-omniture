import requests
import binascii
import time
import hashlib
import json
from datetime import datetime
from .elements import Value, Element, Segment
from .query import Query
import base64
import os
from math import floor

import omniture.utils as utils

# encoding: utf-8

def gen_nonce(length):
   """ Generates a random string of bytes, base64 encoded """
   if length < 1:
      return ''
   string=base64.b64encode(os.urandom(length),altchars=b'-_')
   b64len=4*floor(length)
   if length%3 == 1:
      b64len+=2
   elif length%3 == 2:
      b64len+=3
   return string[0:b64len].decode()

class Account(object):
    DEFAULT_ENDPOINT = 'https://api.omniture.com/admin/1.3/rest/'

    def __init__(self, username, secret, endpoint=DEFAULT_ENDPOINT):
        self.username = username
        self.secret = secret
        self.endpoint = endpoint
        data = self.request('Company', 'GetReportSuites')['report_suites']
        suites = [Suite(suite['site_title'], suite['rsid'], self) for suite in data]
        self.suites = utils.AddressableList(suites)

    def request(self, api, method, query=None):
        if query is None:
            query = {}
        response = requests.post(
            self.endpoint, 
            params={'method': api + '.' + method}, 
            data=json.dumps(query), 
            headers=self._build_token()
            )
        print (response)
        return response.json()

    def _serialize_header(self, properties):
        header = []
        for key, value in properties.items():
            header.append('{key}="{value}"'.format(key=key, value=value))
        return ', '.join(header)

    def _build_token(self):

        nonce = gen_nonce(64)
        nonce_d64 = base64.b64encode(nonce.encode()).decode()
        created = datetime.today().isoformat() + 'Z'
        code = nonce + created + self.secret

        passwd = base64.b64encode(hashlib.sha1(code.encode()).digest()).decode()


        properties = {
            "Username": self.username, 
            "PasswordDigest": passwd,
            "Nonce": nonce_d64,
            "Created": created,
        }
        header = 'UsernameToken ' + self._serialize_header(properties)
        print(header)

        return {'X-WSSE': header}


class Suite(Value):
    def request(self, api, method, query=None):
        if query is None:
            query = {}
        raw_query = {}
        raw_query.update(query)
        if 'reportDescription' in raw_query:
            raw_query['reportDescription']['reportSuiteID'] = self.id
        elif api == 'ReportSuite':
            raw_query['rsid_list'] = [self.id]

        return self.account.request(api, method, raw_query)

    def __init__(self, title, id, account):
        super(Suite, self).__init__(title, id, account)

        self.account = account

    @property
    @utils.memoize
    def metrics(self):
        data = self.request('ReportSuite', 'GetAvailableMetrics')[0]['available_metrics']
        return Value.list('metrics', data, self, 'display_name', 'metric_name')

    @property
    @utils.memoize
    def elements(self):
        data = self.request('ReportSuite', 'GetAvailableElements')[0]['available_elements']
        return Element.list('elements', data, self, 'display_name', 'element_name')

    @property
    @utils.memoize
    def evars(self):
        data = self.request('ReportSuite', 'GetEVars')[0]['evars']
        return Value.list('evars', data, self, 'name', 'evar_num')

    @property
    @utils.memoize
    def segments(self):
        data = self.request('ReportSuite', 'GetSegments')[0]['sc_segments']
        return Segment.list('segments', data, self, 'name', 'id')

    @property
    def report(self):
        return Query(self)

