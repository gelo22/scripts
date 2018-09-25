#!/usr/bin/env python3

import logging
import time
import glob
import json
import os
import sys

class Killer:

    def __init__(self):
        self.conf = json.load(open('{0}/config.yml'.format(os.path.dirname(sys.argv[0]))))
        self.log = logging.getLogger(__name__)
        self.log.setLevel(self.conf['log_level'])
        logging.basicConfig(format=self.conf['log_format'])
        self.log.debug('Config: {0}'.format(self.conf))

    def get_awailable_memory(self):
        metrics_to_found = 2
        metrics_found = 0
        with open('/proc/meminfo') as mem_file:
            for line in mem_file:
                if line.lower().startswith('memfree:'):
                    mem_free = int(line.split()[1]) / 1024
                    metrics_found += 1
                if line.lower().startswith('cached:'):
                    mem_cached = int(line.split()[1]) / 1024
                    metrics_found += 1
                if metrics_found == metrics_to_found:
                    self.mem_free = mem_free + mem_cached
                    self.log.debug('Available memory: {0}'.format(self.mem_free))
                    return

    def find_target_procs(self):
        self.pids = list()
        com_files = glob.glob('/proc/*/comm')
        pat = self.conf['pattern']
        for f_name in com_files:
            with open(f_name) as f:
                cmd_line = f.readline()
            if cmd_line.find(pat) != -1:
                pid = os.path.basename(os.path.dirname(f_name))
                self.pids.append(int(pid))
        self.log.debug('Matched Pids: {0}'.format(self.pids))

    def kill_procs(self):
        self.find_target_procs()
        for pid in self.pids:
            self.log.info('Killing pid {0}'.format(pid))
            os.kill(pid, 9)
        
    def run(self):
        while True:
            self.get_awailable_memory()
            if self.mem_free < self.conf['memory_limit']:
                self.kill_procs()
            time.sleep(self.conf['check_interval'])

if __name__ == '__main__':
    C = Killer()
    C.run()

