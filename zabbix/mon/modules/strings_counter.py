#!/usr/bin/env python

# Unpa

import re
import os
import sys
import datetime
import os.path
import json

from core.base_module import Base_check

class Check(Base_check):

    def __init__(self, args):
        self.args = args
        self._get_conf()
        # for tests indication
        if len(sys.argv) >= 3 and sys.argv[2] == 'test':
            self.test = 1
        else:
            self.test = 0
        # skip checks if file not exist
        self.file_name = self.conf['file_name']
        if not os.path.isfile(self.file_name):
            self.skip = 1
        else:
            self.skip = 0
            self.file_size = os.stat(self.file_name)[6]
            self.file_mtime = os.stat(self.file_name)[8]
        # set time patterns
        self.date_pat = re.compile(r'(\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2})')
        self.time_ago = int(self.conf['time_ago'])
        self.date_now = datetime.datetime.now()
        self.date_now_str = self.date_now.isoformat()[:-7]
        self.start_date = self.date_now - datetime.timedelta(seconds=self.time_ago)
        self.start_date_str = self.start_date.isoformat()[:-7]

    def _find_date(self):
        '''Find bite position in file which close enough for given date pattern'''
        pos = self.file_size / 2
        self.step = self.file_size / 2
        self._find_date_step(pos)
        self.start_pos = self.stop_pos = False
        self.positions = list()
        with open(self.file_name) as data:
            while datetime.datetime.now() - self.date_now < datetime.timedelta(seconds=10):
                self.positions.append(pos)
                old_step = self.step
                self.step = self.step / 2
                if self.step < 1000:
                    if self.test:
                        print 'performed bite steps ', self.positions
                    if pos <= 0 or self.direction == None:
                        self.start_pos = 0
                        return
                    elif self.direction == 'forward':
                        self.start_pos = pos
                        return
                    elif self.direction == 'backward':
                        self.start_pos = pos - old_step
                        if pos <= 0:
                            self.start_pos = 0
                        self.stop_pos = pos
                        return
                if self.direction == 'forward':
                    pos = pos + self.step
                    self._find_date_step(pos)
                elif self.direction == 'backward':
                    pos = pos - self.step
                    self._find_date_step(pos)

    def _find_date_step(self, pos):
        '''Find line with needed date'''
        with open(self.file_name) as data:
            data.seek(pos)
            line = data.readline()
            if not line:
                self.step = 0
            for i in range(11):
                if not self.date_pat.match(line):
                    line = data.readline()
                else:
                    break
            if self.date_pat.match(line):
                line_date = datetime.datetime.strptime(self.date_pat.match(line).group(1), '%Y-%m-%dT%H:%M:%S')
                if line_date <= self.start_date:
                    self.direction = 'forward'
                else:
                    self.direction = 'backward'
            else:
                self.step = 0
                self.direction = None
                if self.test:
                    print 'more than 10 lines not match pattern, exit'

    def _count_lines(self):
        ''' Count lines with matched timestamp'''
        efficiensy_counter = 0
        self._find_date()
        self.line_counter = 0
        with open(self.file_name) as file:
            file.seek(self.start_pos)
            line = 1
            while line:
                efficiensy_counter +=1
                line = file.readline() 
                if not line:
                    continue
                if self.line_counter:
                    self.line_counter += 1
                    continue
                elif self.date_pat.match(line):
                    line_date = datetime.datetime.strptime(self.date_pat.match(line).group(1), '%Y-%m-%dT%H:%M:%S')
                else:
                    continue
                if line_date >= self.start_date:
                    self.line_counter += 1
            self.sender_data['number_of_lines'] = self.line_counter
            if self.test:
                print 'start_pos ', self.start_pos
                print 'efficiensy_counter ', efficiensy_counter

    def run(self):
        if not self.skip:
            self._count_lines()
            self._send()
        else:
            self.sender_data['number_of_lines'] = 0
            self._send()

if __name__ == '__main__':
    C = Check()
    C.run()

