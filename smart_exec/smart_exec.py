#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import subprocess
import sys
import os
import time
import argparse

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('--la_max', type=float, required=True, help='max allowed LA for system, if current LA >= la_max, then command execution will be paused')
parser.add_argument('--sleep_interval', type=float, default=0.5, help='interrupt command execution with this interval in seconds, even if other stop checks allow execution (0.5 is minimal allowed value)')
parser.add_argument('--command', required=True, help='command which will be executed by this script, group of commands with pipes is not allowed')
parser.add_argument('--debug', action='store_const', const=True, help='enable debug mode - print debug messages to stdout')
parser.add_argument('--no_renice', action='store_const', const=True, help='disable renice mode for subprocess, because by default subprocess will be reniced to lowest priority nice=19 ionice=3')
parser.add_argument('--nice', type=int, default=19, help='nice value for subprocess')
parser.add_argument('--ionice', type=int, default=3, help='ionice value for subprocess')
parser.add_argument('--log_file', default='stdout', help='set log file for subprocess output, by default print to stdout')
args = parser.parse_args()

# init config dictionary
conf = dict()

# add parsed args to config dictionary
for key in vars(args):
    if vars(args)[key]:
        conf[key] = vars(args)[key]

def exec_proc(command):
    '''
    execute command without lock operation
    '''
    command = command.split()

    # set CPU and I/O priority for subproocess
    if not conf.get('no_renice'):
        priority_prefix = "ionice -c {} nice -n {}".format(conf['ionice'], conf['nice'])
        command = priority_prefix.split() + command

    # chose output
    if conf['log_file'] == 'stdout':
        stdout_file = sys.stdout
    else:
        stdout_file = open(conf['log_file'], 'w')

    proc = subprocess.Popen(command, stdout=stdout_file, stderr=subprocess.STDOUT)

    return proc

def check_la():
    '''
    Check current LA for system
    '''
    la_file_name = '/proc/loadavg'
    with open(la_file_name) as la_file:
        la = float(la_file.readline().split()[0])
        return la

def pause_proc(instance):
    '''
    Send STOP signal for subprocess instance
    '''
    try:
        instance.send_signal(19)
    except OSError:
        return_code = instance.poll()
        do_log('return_code is: {0}'.format(return_code))
        sys.exit(0)

def resume_proc(instance):
    '''
    Send CONT signal for subprocess instance
    '''
    try:
        instance.send_signal(18)
    except OSError:
        return_code = instance.poll()
        do_log('return_code is: {0}'.format(return_code))
        sys.exit(0)

def do_log(message):
    '''
    Write logs if debug mode
    '''
    if conf.get('debug'):
        sys.stdout.write(message + '\n')
        sys.stdout.flush()

def is_proc_running(instance):
    '''
    Check if proc running
    '''
    return_code = instance.poll()
    if return_code == 0:
        return False
    elif return_code != None:
        do_log('return_code is not 0: {0}'.format(return_code))
        return False
    else:
        return True

# main part
if __name__ == '__main__':
    try:
        # init proc_state
        proc_state = 'resumed'
        # show arguments dictionary in debug mode
        do_log(str(conf))
        # run command, which provided as argument
        proc = exec_proc(conf['command'])

        # main loop with logic, break if command have return code
        while True:
            # check if proc still running
            if not is_proc_running(proc):
                break
            # check current LA
            la = check_la()
            # pause process if LA >= la_max
            if la >= conf['la_max']:
                if proc_state == 'resumed':
                    pause_proc(proc)
                    proc_state = 'paused'
                    do_log('paused by la_max')
            else:
                if proc_state == 'paused':
                    resume_proc(proc)
                    proc_state = 'resumed'
                    do_log('resumed by la_max')
            do_log('la= ' + str(la))
            # pause process if 'sleep_interval' is valid number
            if conf['sleep_interval'] >= 0.5:
                if proc_state == 'resumed':
                    pause_proc(proc)
                    do_log('paused by sleep_interval')
                    time.sleep(conf['sleep_interval'])
                    resume_proc(proc)
                    do_log('resumed by sleep_interval')
                    time.sleep(conf['sleep_interval'])
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        proc.kill()

