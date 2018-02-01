#!/usr/bin/env python

import sys
import importlib
import argparse
from modules.core.base_module import Base_check

class Starter(Base_check):

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--module', help='Module name, wich this engine will execute')
        parser.add_argument('--test', action='store_true', help='module will be executed in test mode - will not send data, only print to stdout')
        parser.add_argument('--discovery', action='store_true', help='module will be executed in discovery mode - will not send data, only print json to stdout')
        parser.add_argument('--conf', default=False, nargs='*', help='Add values to config dictionary, which accessible from module, will override values from module config if it exists')
        parser.add_argument('--servers', default=False, nargs='*', help='Zabbix servers list of IPs or|and domains, which sender will use as destination servers')
        parser.add_argument('--sender_optimize', default=False, type=int, help='Provide interval in minutes - sender will send diffs. All items will send only once per interval.')
        parser.add_argument('--multisrv', action='store_true', help='sender will send data to multiple servers if agent config have more than one')
        self.args = parser.parse_args()

    def _run_module(self):
        check = importlib.import_module('modules.' + self.args.module).Check(self.args)
        check.run()
        
    def run(self):
        if self.args.test:
            self._run_module()
        else:
            try:
                self._run_module()
            except:
                print 0
                sys.exit(1)

if __name__ == '__main__':
    C = Starter()
    C.run()

