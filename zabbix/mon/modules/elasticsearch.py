#!/usr/bin/env python

import urllib2
import json

from core.base_module import Base_check

class Check(Base_check):
    '''Parse elastic status via http json output'''

    def __init__(self, args):
        '''Get agrguments, get data from module's config and command line arguments'''
        self.args = args
        self._get_conf()

    def _proces_checks(self):
        '''Get processes stats'''
        req = urllib2.Request('http://' + self.conf['process_url'])
        resp = urllib2.urlopen(req)
        self.process = resp.read()

    def _health_checks(self):
        '''Get health stats'''
        req = urllib2.Request('http://' + self.conf['health_url'])
        resp = urllib2.urlopen(req)
        self.health = resp.read()

    def _parse_process(self):
        tmp = json.loads(self.process)
        for node in tmp['nodes']:
            if tmp['nodes'][node]['name'] == self.conf['node_name']:
                myhost = node

        self.sender_data['cpu_percent'] = tmp['nodes'][myhost]['process']['cpu']['percent']
        self.sender_data['mem_total_virtual_in_bytes'] = tmp['nodes'][myhost]['process']['mem']['total_virtual_in_bytes']

    def _parse_health(self):
        tmp = json.loads(self.health)
        if tmp['status'] == 'green':
            status = 1
        else:
            status = 0
        self.sender_data['status'] = status
        self.sender_data['unassigned_shards'] = tmp['unassigned_shards']
        self.sender_data['delayed_unassigned_shards'] = tmp['delayed_unassigned_shards']

    def run(self):
        self._proces_checks()
        self._parse_process()
        self._health_checks()
        self._parse_health()
        self._send()

if __name__ == '__main__':
    C = Check()
    C.run()

