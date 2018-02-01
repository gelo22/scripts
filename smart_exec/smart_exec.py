#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from subprocess import PIPE, Popen
import sys
import os
import time
import threading
import argparse

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('--la_max', type=float, required=True, help='max allowed LA for system, if current LA >= la_max, then command execution will be paused')
parser.add_argument('--command', required=True, help='command which will be executed by this script, group of commands with pipes is not allowed')
parser.add_argument('--debug', action='store_const', const=True, help='enable debug mode - print debug messages to stdout')
parser.add_argument('--debug_log_file', default='stdout', help='set log file for debug output, by default print to stdout')
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
    do_log(' '.join(command), 'debug')

    proc = Popen(command, stdout=PIPE, stderr=PIPE)

    # write proc instance to data exchange point
    data['proc_instance'] = proc

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
    instance.send_signal(19)

def resume_proc(instance):
    '''
    Send CONT signal for subprocess instance
    '''
    instance.send_signal(18)

def open_log(file_name, debug_file_name):
    '''
    Open log file if provided
    '''
    if conf['log_file'] != 'stdout':
        data['output'] = open(file_name, 'a')
    else:
        data['output'] = sys.stdout
    if conf['debug_log_file'] != 'stdout':
        data['debug_output'] = open(debug_file_name, 'a')
    else:
        data['debug_output'] = sys.stdout


def do_log(message, level):
    '''
    Write logs if debug mode
    '''
    if level != 'debug':
        data['output'].write(message)
        data['output'].flush()
    elif conf.get('debug'):
        data['debug_output'].write(message + '\n')
        data['debug_output'].flush()

def receive_subprocess_output(instance, source):
    '''Thread for receiving messages from subprocess'''
    messages_source = instance.__getattribute__(source)
    line = True
    while line:
        line = messages_source.readline()
        if sys.version_info.major == 2:
            message = line
        else:
            message = bytes.decode(line)
        do_log(message, 'command_' + source)
    data['threads_done'] += 1

# main part
if __name__ == '__main__':
    try:
        # init dictionary for data exchange
        data = dict()
        # open log file(s) if needed
        open_log(conf['log_file'], conf['debug_log_file'])
        # show arguments dictionary in debug mode
        do_log(str(conf), 'debug')
        # init return code value
        data['threads_done'] = 0
        # run command, which provided as argument
        exec_proc(conf['command'])
        # run thread for messages collection from command stdout
        receive_command_stdout_thread = threading.Thread(target=receive_subprocess_output, args=(data['proc_instance'], 'stdout',))
        receive_command_stdout_thread.daemon = True
        receive_command_stdout_thread.start()
        # run thread for messages collection from command stderr
        receive_command_stderr_thread = threading.Thread(target=receive_subprocess_output, args=(data['proc_instance'], 'stderr',))
        receive_command_stderr_thread.daemon = True
        receive_command_stderr_thread.start()

        # init proc_state value
        data['proc_state'] = 'resumed'
        # main loop with logic, break if command have return code
        while data['threads_done'] == 0:
            la = check_la()
            # stop process if LA >= la_max
            if la >= conf['la_max']:
                if data['proc_state'] == 'resumed':
                    pause_proc(data['proc_instance'])
                    data['proc_state'] = 'paused'
                    do_log('paused', 'debug')
                else:
                    do_log('already_paused', 'debug')
            else:
                if data['proc_state'] == 'paused':
                    resume_proc(data['proc_instance'])
                    data['proc_state'] = 'resumed'
                    do_log('resumed', 'debug')
                else:
                    do_log('already_resumed', 'debug')
            do_log('la= ' + str(la), 'debug')
            time.sleep(1)
    except KeyboardInterrupt:
        # this will fix deadlock from subprocess
        data['proc_instance'].kill()
        data['proc_instance'] = None
        time.sleep(1)
        sys.exit(0)
    time.sleep(1)
    sys.exit(0)

