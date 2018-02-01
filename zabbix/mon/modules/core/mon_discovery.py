#!/usr/bin/env python

import sys
import json
from subprocess import Popen, PIPE

class Mon_discovery:

    def __init__(self, args, sender_data):
        self.args = args
        self.sender_data = sender_data

    def _make_json(self):
        '''Return JSON for discovery rule'''
        data = { 'data':[] }
        for key in self.sender_data:
            row = { '{#MODULE_NAME}': self.args.module, '{#ITEM_NAME}': key }
            data['data'].append(row)
        print json.dumps(data)

    def run(self):
        '''Run discovery'''
        self._make_json()

