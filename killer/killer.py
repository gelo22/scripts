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
        metrics_to_found = 3
        metrics_found = 0
        with open('/proc/meminfo') as mem_file:
            for line in mem_file:
                if line.lower().startswith('memfree:'):
                    self.mem_free = int(line.split()[1]) / 1024
                    metrics_found += 1
                if line.lower().startswith('cached:'):
                    self.mem_cached = int(line.split()[1]) / 1024
                    metrics_found += 1
                if line.lower().startswith('memavailable:'):
                    self.mem_available = int(line.split()[1]) / 1024
                    metrics_found += 1
                if metrics_found == metrics_to_found:
                    self.log.debug('Available memory: {0}, Cache: {1}'.format(self.mem_free, self.mem_cached))
                    return

    def get_la(self):
        self.la = -1
        with open('/proc/loadavg') as la_file:
            la_tmp = la_file.readline()
            self.la = float(la_tmp.split()[0])
            self.log.debug('LA: {}'.format(self.la))
        if self.la == -1:
            self.log.error('LA not parsed from "/proc/loadavg"')
            sys.exit(0)

    def get_cpu_info(self):
        self.cpu_count = 0
        with open('/proc/cpuinfo') as cpu_info_file:
            for line in cpu_info_file:
                if line.startswith('processor\t:'):
                    self.cpu_count += 1
        self.log.debug('CPU count: {}'.format(self.cpu_count))
        if self.cpu_count == 0:
            self.log.error('CPU info not parsed from "/proc/cpuinfo"')
            sys.exit(0)

    def find_target_procs(self):
        self.pids = dict()
        com_files = glob.glob('/proc/*/comm')
        for index, proc in enumerate(self.conf['procs_to_kill']):
            pat = self.conf['procs_to_kill'][index]['pattern']
            for f_name in com_files:
                with open(f_name) as f:
                    cmd_line = f.readline()
                if cmd_line.find(pat) != -1:
                    pid = int(os.path.basename(os.path.dirname(f_name)))
                    self.pids[pid] = self.conf['procs_to_kill'][index].copy()
        self.log.debug('Matched Pids: {0}'.format(self.pids))

    def kill_procs(self):
        self.find_target_procs()
        self.killed_procs = dict()
        for pid in self.pids:
            kill_code = self.pids[pid]
            os.kill(pid, self.pids[pid]['kill_signal'])
            name = self.pids[pid]['name']
            if name in self.killed_procs:
                self.killed_procs[name].append(pid)
            else:
                self.killed_procs[name] = [pid]
        for name in self.killed_procs:
            self.log.info('{} killed pids: {}'.format(name, self.killed_procs[name]))
        
    def drop_cache(self):
        with open('/proc/sys/vm/drop_caches', 'w') as drop_cache_file:
            drop_cache_file.write('3\n')

    def run(self):
        while True:
            self.get_awailable_memory()
            self.get_la()
            self.get_cpu_info()
            if self.mem_cached < self.conf['cached_limit']:
                self.drop_cache()
                self.log.info('Cache dropped')
                time.sleep(self.conf['check_interval'])
            if self.mem_available < self.conf['memory_limit']:
                self.log.info(
                    'mem_free: {} < memory_limit: {} and mem_cached: {} < cached_minimum: {}'.format(
                        self.mem_free,
                        self.conf['memory_limit'],
                        self.mem_cached,
                        self.conf['cached_minimum']
                    )
                )
                self.kill_procs()
            elif self.la > self.cpu_count + 1:
                self.log.info(
                    '{} > {}'.format(
                        self.la,
                        self.cpu_count
                    )
                )
                self.kill_procs()
            time.sleep(self.conf['check_interval'])

if __name__ == '__main__':
    C = Killer()
    C.run()

