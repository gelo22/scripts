#!/usr/bin/env python

import urllib2
import csv
import re
import json

from core.base_module import Base_check

class Check(Base_check):

    def __init__(self, args):
        self.args = args
        self._get_conf()
        self.url = 'http://' + self.conf['url'].replace('+', ';')
        self.items = self.conf['items'].split('+')
        self.pxnames = self.conf['pxnames'].split('+')

    def _url_check(self):
        req = urllib2.Request(self.url)
        self.resp_page = urllib2.urlopen(req)

    def _parse(self):
        data = list()
        for n in csv.reader(self.resp_page):
            data.append(n)
        for i in range(1, len(data)):
            for ii in range(2, len(data[0])):
                pxname = data[i][0]
                if pxname not in self.pxnames:
                    break
                svname = data[i][1]
                item = data[0][ii]
                if item not in self.items:
                    continue
                key = '%s_%s_%s' % (pxname, svname, item)
                val = data[i][ii]
                if len(val) == 0:
                    continue
                for pat in self.items:
                    if key.find(pat) != -1:
                        if pat == '_status':
                            if val.lower() == 'up':
                                val = '1'
                            else:
                                val = '0'
                        if pat == '_lastsess':
                            if val.lower() == '-1':
                                val = '0'
                        self.sender_data[key.lower()] = val.lower()
                        break

    def _discovery(self):
        '''Return JSON for discovery rule'''
        data = { 'data':[] }
        for key in self.sender_data:
            if key.find('frontend') != -1:
                row = { '{#MODULE_NAME}': self.args.module, '{#ITEM_NAME}': key, '{#SOURCE_NAME}': 'frontend' }
            elif key.find('backend') != -1:
                row = { '{#MODULE_NAME}': self.args.module, '{#ITEM_NAME}': key, '{#SOURCE_NAME}': 'backend' }
            else:
                row = { '{#MODULE_NAME}': self.args.module, '{#ITEM_NAME}': key, '{#SOURCE_NAME}': 'server' }
            data['data'].append(row)
        print json.dumps(data)

    def run(self):
        self._url_check()
        self._parse()
        if self.args.discovery:
            self._discovery()
        else:
            self._send()

if __name__ == '__main__':
    C = Check()
    C.run()

