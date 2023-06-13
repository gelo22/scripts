#!/usr/bin/env python

import urllib.request
import json

base_url = 'http://127.0.0.1:3000'
api_key = 'Bearer 0000000000000000000000000000000000000000000000000000000000000000000000000000'
output_file = './dashboards.yaml'
data = dict()
data['uids'] = list()
data['dashboards'] = list()

def get_dashboards_uid():
    '''Get uid of each dashboard'''
    url = base_url + '/api/search/'
    req = urllib.request.Request(url)
    req.add_header('Authorization', api_key.encode())
    response = urllib.request.urlopen(req, timeout=10)
    dashboards = json.loads(response.read().decode())
    for d in dashboards:
        data['uids'].append(d['uid'])

def get_dashboard(uid):
    '''Get dashboard'''
    url = base_url + '/api/dashboards/uid/' + uid
    req = urllib.request.Request(url)
    req.add_header('Authorization', api_key.encode())
    response = urllib.request.urlopen(req, timeout=10)
    data['dashboards'].append(json.loads(response.read().decode()))

get_dashboards_uid()
for uid in data['uids']:
    get_dashboard(uid)

with open(output_file, 'w') as f:
    json.dump(data['dashboards'], f)
