#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import subprocess
import sys
import json
import os
import time

def exec_proc(task):
    '''
    execute command without lock operation
    '''
    # replace {log_file} in command by log file
    for i in range(len(task['command'])):
        if '{log_file}' in task['command'][i]:
            task['command'][i] = conf['log_dir'] + task['command'][i].format(log_file=task['log_file'])
    # write output to log only if command has no own logging
    if task['subprocess_log']:
        output = open(conf['log_dir'] + task['log_file'], 'w')
    else:
        output = subprocess.PIPE
    print('Running: "{0}"'.format(' '.join(task['command'])))
    proc = subprocess.Popen(task['command'], stdout=output, stderr=subprocess.STDOUT)
    return proc

def get_la():
    '''
    Get current LA 1 for system
    '''
    with open(conf['la_file_name']) as la_file:
        la = float(la_file.readline().split()[0])
        return la

def get_mem_free():
    '''
    Get current memory stats for system
    '''
    with open(conf['mem_file_name']) as mem_file:
        for line in mem_file:
            if line.startswith('MemFree:'):
                mem_free = int(line.split()[1]) / 1024
                return mem_free

def collect_data():
    '''
    Collect data by defined tasks
    '''
    # create log dir if needed
    if not os.path.exists(conf['log_dir']):
        os.mkdir(conf['log_dir'])
    for task in conf['tasks']:
        if os.path.exists(conf['log_dir'] + task['log_file']):
            os.remove(conf['log_dir'] + task['log_file'])
        procs.append(exec_proc(task))

# main part
if __name__ == '__main__':
    conf = json.load(open(sys.argv[0] + '.conf'))
    # fork if daemon mode
    if conf['daemon']:
        if os.fork():
            sys.exit()
        # open log file
        sys.stdout = open(conf['log_file'], 'w')
        sys.stderr = sys.stdout
    # write pid file
    with open(conf['pid_file'], 'w') as pid:
        pid.write(str(os.getpid()))
    procs = list()
    triggered = False
    try:
        while True:
            print('tst')
            if get_la() > conf['triggers']['la_max'] or get_mem_free() < conf['triggers']['mem_free']:
                if not triggered:
                    procs = list()
                    collect_data()
                    triggered = True
                else:
                    time.sleep(conf['trigger_reload_time'])
                    triggered = False
            sys.stdout.flush()
            if conf['sleep_interval'] > 0.5:
                time.sleep(conf['sleep_interval'])
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        for proc in procs:
            proc.kill()

