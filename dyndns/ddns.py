#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import re
import json
import argparse
import traceback
import socket

# python 2 and 3 version compatibility
if sys.version_info.major == 2:
    import urllib2
else:
    import urllib.request as urllib2

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('--host_name', default=False, help='host name which must be updated')
parser.add_argument('--config', default=sys.argv[0] + '.conf', help='config file location')
parser.add_argument('--address', help='use this address and skip ip detection from ssh')
parser.add_argument('--debug', default=False, help='enable debug mode')
args = parser.parse_args()

class Ddns:
    '''Class for records changes via namesilo.com api'''

    def __init__(self, args):
        # get config from json file
        self.conf = json.load(open(args.config))
        # add parsed args to config dictionary
        for key in vars(args):
            self.conf[key] = vars(args)[key]
        self.file_name = self.conf['log_directory'] + '/' + self.conf['host_name']

    def _get_last_data(self):
        '''Read data from last run if exist'''
        if not os.path.isdir(self.conf['log_directory']):
            os.mkdir(self.conf['log_directory'], int('0755', base=8))
        # read last ip of host if data exist
        if not os.path.isfile(self.file_name):
            self.last_ip = False
            return
        with open(self.file_name, 'r') as data_file:
            self.last_ip = data_file.readline().strip()

    def _get_own_ip(self):
        '''Get own IP-address if updating own record'''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        self.ip = s.getsockname()[0]
        s.close()

    def _validate_ip(self):
        '''Validate IP-address'''
        nums = self.ip.split('.')
        for n in nums:
            num = int(n)
            if num < 0 and num > 255:
                print('IP: {0} is not valid'.format(self.ip))
                sys.exit(1)

    def _get_data(self):
        '''Get IP-address of remote client'''
        if args.address:
            if args.address == 'me':
                self._get_own_ip()
            else:
                self.ip = args.address
                self._validate_ip()
        else:
            client = os.environ['SSH_CONNECTION']
            self.ip = client.split()[0]

    def _write_data(self):
        '''Write IP-address of remote client to file for future usage'''
        with open(self.file_name, 'w') as data_file:
            data_file.write(self.ip)

    def _is_host_allowed(self):
        '''Check if host allowed to DNS registration'''
        if self.conf['host_name'] not in self.conf['allowed_hostnames']:
            if self.conf['debug']:
                print(self.conf['host_name'] + ' not in allowed hosts')
            sys.exit(0)

    def _prepare_url(self):
        '''Prepare URL for hosting API regarding to data from config'''
        update_record_url = self.conf['api_url'] + 'dnsUpdateRecord?version=1&type=xml&key={0}&domain={1}&rrid={2}&rrtype={3}&rrhost={4}&rrvalue={5}&rrttl={6}'
        add_record_url = self.conf['api_url'] + 'dnsAddRecord?version=1&type=xml&key={0}&domain={1}&rrtype={3}&rrhost={4}&rrvalue={5}&rrttl={6}'
        if self.record_id:
            base_url = update_record_url
        else:
            base_url = add_record_url
        self.url = base_url.format(self.conf['user_key'], self.conf['root_domain'], self.record_id, self.conf['entry_type'], self.conf['host_name'], self.ip, self.conf['entry_ttl'])

    def _use_api(self):
        '''Request sesulting URL and read response'''
        self.req = req = urllib2.Request(self.url, None, self.conf['http_headers'])
        self.resp = resp = urllib2.urlopen(req)
        self.resp_page = resp.read()

    def _write_log(self, message):
        '''Write message to log file'''
        with open(self.file_name + '.log', 'w') as data_file:
            data_file.write(message + '\n')

    def is_address_changed(self):
        '''Check if address changed from last run'''
        if self.last_ip != self.ip:
            return True

    def _get_domain_list(self):
        '''Get current domains list from via hosting API'''
        domain_pat = re.compile(r'<resource_record><record_id>(?P<id>[a-zA-Z0-9]+)</record_id><type>[A-Z]+</type><host>' +
                         '.'.join((self.conf['host_name'], self.conf['root_domain'])) + 
                         r'</host><value>[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}</value>' +
                         r'<ttl>[0-9]+</ttl><distance>[0-9]+</distance></resource_record>')
        self.url = self.conf['api_url'] + 'dnsListRecords?version=1&type=xml&key={0}&domain={1}'.format(self.conf['user_key'], self.conf['root_domain'])
        self.req = req = urllib2.Request(self.url, None, self.conf['http_headers'])
        self.resp = resp = urllib2.urlopen(req)
        for line in resp:
            line = bytes.decode(line)
            parsed_line = domain_pat.search(line)
            if parsed_line:
                self.record_id = parsed_line.groupdict().get('id')
                if not self.record_id:
                    self._write_log('domain founded but id parsing failed\n')
                    sys.exit(0)
            else:
                self.record_id = False

    def run(self):
        '''Run all things together'''
        self._get_last_data()
        self._get_data()
        if self.is_address_changed():
            self._get_domain_list()
            self._is_host_allowed()
            self._prepare_url()
            self._use_api()
            self._write_log(bytes.decode(self.resp_page) + '\n')
            self._write_data()
        else:
            self._write_log('client`s ip not changed since last run\n')
            sys.exit(0)
        
if __name__ == '__main__':
    # run in debug mode if debug option is set
    if args.debug:
        C = Ddns(args)
        C.run()
    else:
        try:
            C = Ddns(args)
            C.run()
        except:
            pass

