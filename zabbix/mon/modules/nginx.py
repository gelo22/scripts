#!/usr/bin/env python

import urllib2
import re

from core.base_module import Base_check

class Check(Base_check):

    def __init__(self, args):
        self.args = args
        self.keys = ['active_connections', 'server_accepts', 'server_handled', 'server_requests', 'reading', 'writing', 'waiting']
        self.pat = re.compile(r'''active\s+connections\:\s+
                             (?P<active_connections>\d+)\s+server\s+accepts\s+handled\s+requests\s+
                             (?P<server_accepts>\d+)\s+
                             (?P<server_handled>\d+)\s+
                             (?P<server_requests>\d+)\s+reading:\s+
                             (?P<reading>\d+)\s+writing:\s+
                             (?P<writing>\d+)\s+waiting:\s+
                             (?P<waiting>\d+)''', re.MULTILINE | re.VERBOSE)

    def _url_check(self):
        req = urllib2.Request('http://' + self.conf['url'])
        resp = urllib2.urlopen(req)
        self.resp_page = resp.read()

    def _parse(self):
       resp_page = self.resp_page.lower().strip()
       if self.pat.search(resp_page):
           for key in self.keys:
               self.sender_data[key] = self.pat.search(resp_page).group(key)

    def run(self):
        self._get_conf()
        self._url_check()
        self._parse()
        self._send()

if __name__ == '__main__':
    C = Check()
    C.run()

