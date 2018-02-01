#!/usr/bin/env python

import sys
import os
import datetime
from subprocess import Popen, PIPE

class Mon_sender():

    def __init__(self, args, sender_data):
        '''Set item name pattern, etc'''
        os.umask(int('137', base=8))
        self.args = args
        self.sender_data = sender_data
        self.user_id = str(os.geteuid())
        self.item_pat = '%s mon[%s,%s] %s\n'
        self.file_name = '/tmp/zabbix_sender_%s_%s_' % (self.args.module, self.user_id)
        self.data_file =  '%s_diff_' % (self.file_name)
        self.date_file =  '%s_date_' % (self.file_name)
        self.trend_interval = self.args.sender_optimize * 60

    def _get_zabbix_params(self):
        '''Get get zabbix sender params from config and arguments'''
        with open('/etc/zabbix/zabbix_agentd.conf') as conf:
            for line in conf:
                if line.startswith('Server='):
                    srv_tmp = line.split('=')[1].split(',')
                    self.dst_servers = [i.strip() for i in srv_tmp]
                if line.startswith('Hostname='):
                    self.src_host = line.split('=')[1].rstrip()
            if self.args.servers:
                self.dst_servers = self.args.servers
            if not self.args.multisrv:
                self.dst_servers = self.dst_servers[:1]
        postfix = self.dst_servers[0].replace('.','_')
        self.file_name += postfix
        self.data_file += postfix
        self.date_file += postfix

    def _get_old_data(self):
        '''Get data from last module run'''
        self.sender_data_old = dict()
        if os.path.isfile(self.data_file):
            with open(self.data_file, 'r') as file:
                for line in file:
                    line = line.split('=')
                    key = line[0]
                    val = line[1].rstrip()
                    self.sender_data_old[key] = val

    def _save_new_data(self):
        '''Save new data for _get_old_data()'''
        with open(self.data_file, 'w') as diff_file:
            for key in self.sender_data:
                line = '%s=%s\n' % (key, self.sender_data[key])
                diff_file.write(line)

    def _diff_data(self):
        '''Compare last check data vs current and add to sender_data only difference'''
        self._save_date()
        if self._send_trend():
            return
        self._get_old_data()
        self._save_new_data()
        self.sender_data_new = dict()
        for key in self.sender_data:
            if self.sender_data_old.get(key, False) == str(self.sender_data[key]):
                continue
            else:
                self.sender_data_new[key] = self.sender_data[key]
        if self.sender_data_new != self.sender_data:
            self.sender_data = self.sender_data_new

    def _save_date(self):
        '''Save date of last full data send'''
        self.date_now = datetime.datetime.now()
        if os.path.isfile(self.date_file):
            return
        with open(self.date_file, 'w') as file:
            file.write(str(self.date_now))

    def _send_trend(self):
        '''Return True if last full data send is more than N minutes ago'''
        self.trend_date_interval = self.date_now - datetime.timedelta(seconds=self.trend_interval)
        with open(self.date_file, 'r') as file:
            for line in file:
                self.old_date = datetime.datetime.strptime(line, '%Y-%m-%d %H:%M:%S.%f')
                if self.old_date < self.trend_date_interval:
                    os.unlink(self.date_file)
                    return True
        

    def _send(self):
        '''Collect data to file and send it to zabbix server'''
        file_name = self.file_name
        for server in self.dst_servers:
            with open(file_name, 'w') as file:
                for key in self.sender_data:
                    val = str(self.sender_data[key])
                    line = self.item_pat % (self.src_host, self.args.module, key, val)
                    if self.args.test:
                        print line,
                        continue
                    file.write(line)
                line = self.item_pat % (self.src_host, self.args.module, 'module_status', '1')
                file.write(line)
                if self.args.test:
                    print line
                args = ['zabbix_sender', '-vv', '-z', server, '-i', file_name]
            if self.args.test:
                print ' '.join(args)
            else:
                proc0 = Popen(args, stdout=PIPE, stderr=PIPE)
                proc = proc0.communicate()
                proc0.wait()

    def _discovery(self):
        '''Run discovery'''
        from mon_discovery import Mon_discovery
        Mon_discovery(self.args, self.sender_data).run()

    def run(self):
        '''Run sender'''
        if self.args.discovery:
            self._discovery()
            return
        self._get_zabbix_params()
        if self.args.sender_optimize:
            self._diff_data()
        self._send()

