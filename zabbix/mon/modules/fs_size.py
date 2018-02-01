#!/usr/bin/env python

from subprocess import PIPE, Popen
from core.base_module import Base_check

class Check(Base_check):

    def __init__(self, args):
        '''Get agrguments, get data from module's config and command line arguments'''
        self.args = args
        self._get_conf()
        self.fs_exclude = self.conf['fs_exclude'].split('+')
        self.formating = ''.join(['%.', self.conf['precision'],'f'])

    def _parse_fstab(self):
        '''Parse /etc/fstab'''
        self.fstab_list = list()
        with open('/etc/fstab') as fstab:
            for line in fstab:
                line = line.split()
                if line[0].startswith('#') or len(line) != 6:
                    continue
                fs_type = line[2].split(',')[0]
                if fs_type not in self.fs_exclude:
                    mount = line[1]
                    self.fstab_list.append(mount)

    def _parse_df(self):
        '''Parse df, add result to sender'''
        args = '/bin/df'
        proc0 = Popen(args, stdout=PIPE, stderr=PIPE)
        for line in proc0.stdout:
            line = line.split()
            if len(line) != 6:
                continue
            key = line[5]
            if key in self.fstab_list:
                val = self.formating % (float(line[2]) / float(self.conf['denominator']))
                self.sender_data[key] = val

    def run(self):
        self._parse_fstab()
        self._parse_df()
        self._send()


