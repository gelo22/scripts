#!/usr/bin/env python

import urllib2
import json
from core.base_module import Base_check

class Check(Base_check):

    def _url_check(self):
        req = urllib2.Request('http://' + self.conf['url'])
        resp = urllib2.urlopen(req)
        self.resp_page = resp.read()

    def _parse(self):
        tmp = json.loads(self.resp_page)
        for key in tmp:
            key1 = key.replace(' ', '_')
            self.sender_data[key1] = tmp[key]

    def run(self):
        self._get_conf()
        self._url_check()
        self._parse()
        self._send()

if __name__ == '__main__':
    C = Check()
    C.run()

