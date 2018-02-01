#!/usr/bin/env python2

import sys
import os
from subprocess import Popen, PIPE
import Queue
import threading
import re
import datetime

class Ssh:
    '''This class can access multiple servers via ssh and scp(both direction)'''

    def __init__(self):
        '''Run all methods, which will collect all data for threading'''
        self.args = dict()
        self._get_args()
        self.test = int(self.args.get('test', 0))
        self.script_config_file = './ssh.py_config'
        self._get_args()
        self._parse_ssh_py_config()
        self._parse_hosts_config()
        self._determine_mode()
        if self.test:
            for serv in self.servers:
                command = self._ssh_make_cmd(serv)
                print serv, command
            sys.exit()
        self._pepare_threading()

    def _parse_ssh_py_config(self):
        '''Parse ssh.py config'''
        data = dict()
        pat = re.compile(r'([0-9a-zA-Z\_\-\s]+)=(.*)')
        if not os.path.isfile(self.script_config_file):
            if self.debug:
                print('No config file')
            return
        with open(self.script_config_file) as conf:
            for line in conf:
                if line.startswith('#'):
                    continue
                parsed = pat.search(line)
                if parsed:
                    key = parsed.group(1).strip()
                    val = parsed.group(2).strip()
                    data[key] = val
        for key in data:
            if key not in self.args:
                self.args[key] = data[key]
        if self.debug:
            print('args from config', data)
            print('args from config + cmd', self.args)

    def _get_args(self):
        '''Parse args'''
        data = dict()
        for (num,arg) in enumerate(sys.argv[1:], start=1):
            tmp_arg = arg.split('=')
            if len(tmp_arg) == 2:
                key = tmp_arg[0]
                val = tmp_arg[1]
            else:
                key = 'arg' + str(num)
                val = arg
            data[key] = val
            self.args[key] = val
        self.debug = int(self.args.get('debug', 0))
        if self.debug:
            print('args from cmd', data)

    def _parse_hosts_config(self):
        '''Parse ansible config'''
        servers_lists = self.servers_lists = dict()
        inventory_file = self.args.get('config', './hosts')
        config = open(inventory_file)
        for line in config:
            line = line.strip().split(' ')[0]
            if line.startswith('#'):
                continue
            if line:
                if line.startswith('['):
                    group = self.group = line[1:-1]
                    servers_lists[group] = set()
                    continue
                else:
                    sl = line.split(']')
                    if len(sl) == 1:
                        servers_lists[group].add(line)
                        continue
                    elif not all(sl):
                        res = sl[0].split('[')
                        num = res[1].split(':')
                        n1 = int(num[0])
                        n2 = int(num[1]) + 1
                        for srv_num in range(n1, n2):
                            servers_lists[group].add(res[0] + str(srv_num))
                        continue
                    elif all(sl):
                        res = sl[0].split('[') + [sl[1]]
                        num = res[1].split(':')
                        n1 = int(num[0])
                        n2 = int(num[1]) + 1
                        for srv_num in range(n1, n2):
                            servers_lists[group].add(res[0] + str(srv_num) + res[2])
                        continue
        if self.debug:
            print('hosts', self.servers_lists)

    def _determine_mode(self):
        '''Determin ssh or scp mode. Make resulting servers list for current mode'''
        ssh_pat = re.compile(r'^((?P<user>[a-zA-Z0-9\_\-]+)@)?(?P<servers>[a-zA-Z0-9\_\,\.\[\]\*\+\(\)\{\}\?\^\$\|\-]+)')
        scp_pat = re.compile(r'^((?P<user>[a-zA-Z0-9\_\-]+)@)?(?P<servers>[a-zA-Z0-9\_\,\.\[\]\*\+\(\)\{\}\?\^\$\-]+):(?P<path>[a-zA-Z0-9_\.\/\-]+)$')
        self.mode = self.args.get('mode', 'ssh')
        if self.mode == 'ssh':
            result = ssh_pat.match(self.args.get('arg1', '')).groupdict()
            self.user = result['user']
            if not self.user:
                self.user = self.args.get('user', 'root')
            self.command = self.args.get('arg2', 'uname')
            tmp_servers = result['servers'].split(',')
            if self.debug:
                print('mode', self.mode)
                print('tmp_servers', tmp_servers)
            self._match_servers(tmp_servers)
        elif self.mode == 'scp':
            if self.args['arg1'].find(':') != -1:
                self.direction = 'from'
                result = scp_pat.match(self.args.get('arg1', '')).groupdict()
                self.src = result['path']
                if not self.src:
                    self.src = './tst'
                self.dst = self.args.get('arg2', './')
            elif self.args['arg2'].find(':') != -1:
                self.direction = 'to'
                result = scp_pat.match(self.args.get('arg2', '')).groupdict()
                self.dst = result['path']
                if not self.dst:
                    self.dst = './tst'
                self.src = self.args.get('arg1', './')
            self.user = result['user']
            if not self.user:
                self.user = self.args.get('user', 'root')
            tmp_servers = result['servers'].split(',')
            if self.debug:
                print('mode', self.mode)
                print('tmp_servers', tmp_servers)
            self._match_servers(tmp_servers)

    def _match_servers(self, tmp_servers):
        '''Make final servers list regarding to host,group,regex from inventory + hosts from cmd which not in inventory'''
        self.servers = set()
        re_tmp_servers = set()
        re_chars = '^${}[]*+|()?'
        if not tmp_servers:
            tmp_servers = self.args.get('servers', 'localhost').split(',')
        for server in tmp_servers:
            # check if server name contains regex
            for c in re_chars:
                if server.find(c) != -1:
                    regex = 1
                    re_tmp_servers.add(server)
                    break
                else:
                    regex = 0
            if regex:
                regex = 0
                continue
            # select all servers if server name = all
            if server == 'all':
                for group in self.servers_lists:
                    self.servers = self.servers.union(self.servers_lists[group])
                continue
            # if server name match group - add hosts in group
            if server in self.servers_lists:
                self.servers = self.servers.union(self.servers_lists[server])
            # if host not in config - add as is
            else:
                self.servers.add(server)
        # if any server in list have regex - then only matching servers from non regex servers in list will be in result list
        regex_servers = set()
        if self.debug:
            print('re_tmp_servers', re_tmp_servers)
        if re_tmp_servers:
            for server in re_tmp_servers:
                srv_pat = re.compile(r'%s' % (server))
                for srv in self.servers:
                    if srv_pat.search(srv):
                        regex_servers.add(srv)
            self.servers = regex_servers
        if self.debug:
            print('regex_servers', regex_servers)
            print('servers', self.servers)
        
    def _pepare_threading(self):
        '''Prepare storage and options for threading'''
        self.async = int(self.args.get('async', 0))
        self.threads = range(1, int(self.args.get('threads', 100)) + 1)
        self.ssh_out = { 'stdout': {}, 'stderr': {} }
        self.ssh_out_tmp = dict()
        self.queue = Queue.Queue()
            
    def _ssh_make_cmd(self, server):
        '''Assemble final ssh command for Popen'''
        if self.mode == 'ssh':
            command = ['ssh', self.user + '@' + server, self.command]
        elif self.mode == 'scp':
            if self.direction == 'to':
                command = ['scp', self.src, self.user + '@' + server + ':' + self.dst]
            elif self.direction == 'from':
                command = ['scp', self.user + '@' + server + ':' + self.src, self.dst + '_' + server]
        ssh_options = self.args.get('ssh_options', 'ConnectTimeout=10').split()
        for opt in ssh_options:
            command.insert(1, '-o')
            command.insert(2, opt)
        prefix = self.args.get('ssh_prefix', '')
        if prefix:
            command.insert(0, prefix)
        return command

    def ssh(self, num):
        '''Run ssh or scp to server from list by threads'''
        try:
            queue = self.queue
            while True:
                server = queue.get()
                command = self._ssh_make_cmd(server)
                if num == 1 and self.debug:
                    print 'command:', command
                proc0 = Popen(command, stdout=PIPE, stderr=PIPE)
                proc = proc0.communicate()
                if proc[0]:
                    proc_stdout = proc[0].split('\n')[:-1]
                    self.ssh_out_tmp[num]['stdout'][server] = proc_stdout
                    if self.async:
                        for line in proc_stdout:
                            print server + ' ' + line
                if proc[1]:
                    proc_stderr = proc[1].split('\n')[:-1]
                    self.ssh_out_tmp[num]['stderr'][server] = proc_stderr
                    if self.async:
                        for line in proc_stderr:
                            print server + ' ' + line
                if not any([proc[0], proc[1]]):
                    ret_code = [str(proc0.returncode)]
                    self.ssh_out_tmp[num]['stderr'][server] = ret_code
                    if self.async:
                        for line in ret_code:
                            print server + ' ' + line
                queue.task_done()
        except:
            self.ssh_out_tmp[num]['stderr'][server] = ['exception: ' + str(sys.exc_info()) + 'command: ' + str(command)]
            queue.task_done()
            return

    def stats(self):
        '''Print resulting output'''
        log_file_name = self.args.get('log_file', os.environ['HOME'] + '/ssh.py_out')
        if not self.args.get('no_logs', ''):
            log_file = open(log_file_name, 'aw')
        stdout_sorted = self.ssh_out['stdout'].keys()
        stdout_sorted.sort()
        stderr_sorted = self.ssh_out['stderr'].keys()
        stderr_sorted.sort()
        if not self.args.get('no_logs', ''):
            log_file.write(str(datetime.datetime.now()) + ' =====ssh_py=====\n')
        for server in stdout_sorted:
            for line in self.ssh_out['stdout'][server]:
                out = server + ' ' + line
                if not self.async:
                    print out
                if not self.args.get('no_logs', ''):
                    log_file.write(out + '\n')
        for server in stderr_sorted:
            for line in self.ssh_out['stderr'][server]:
                out = server + ' ' + line
                if not self.async:
                    print out
                if not self.args.get('no_logs', ''):
                    log_file.write(out + '\n')
        if not self.args.get('no_logs', ''):
            log_file.close()

# Main loop
if __name__ == '__main__':
    C = Ssh()
    # threading shit
    target0 = C.ssh
    queue = C.queue
    for num in C.threads: 
        C.ssh_out_tmp[num] = { 'stdout': {}, 'stderr': {} }
        thread = threading.Thread(target=target0, args=(num,))
        thread.daemon = True
        thread.start()

    for server in C.servers:
        queue.put(server)

    queue.join()

    for num in C.threads:
        C.ssh_out['stdout'].update(C.ssh_out_tmp[num]['stdout'])
        C.ssh_out['stderr'].update(C.ssh_out_tmp[num]['stderr'])

    C.stats()
    
