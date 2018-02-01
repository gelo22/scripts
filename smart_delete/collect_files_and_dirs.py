#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import datetime
import argparse

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('--path', required=True, help='path where to search')
parser.add_argument('--debug', default=False, type=bool, help='enable debug mode')
parser.add_argument('--log_file', default='./' + sys.argv[0].split('/')[-1] + '.log', help='write log to file "name"')
args = parser.parse_args()

class Find_files:

    def __init__(self, args):
        self.statistics = dict()
        pass

    def _parse_args(self):
        self.conf = dict()
        for key in vars(args):
            self.conf[key] = vars(args)[key]
        if self.conf['debug']:
            print(self.conf)

    def _open_log(self):
        '''Open log files'''
        self.files_log_file = open(self.conf['log_file'] + '.files', 'w')
        self.dirs_log_file = open(self.conf['log_file'] + '.dirs', 'w')
        self.stats_log_file = open(self.conf['log_file'] + '.stats', 'w')

    def _write_log(self, message, destination):
        '''Write regular message to log, which destination depends from argument'''
        template = "{}\n".format(message.decode('UTF-8'))
        final_message = template.encode('UTF-8')
        if destination == 'files':
            self.files_log_file.write(final_message)
        elif destination == 'dirs':
            self.dirs_log_file.write(final_message)
        elif destination == 'stats':
            self.stats_log_file.write(final_message)

    def _get_stats(self, file_name):
        '''Collect file stats'''
        try:
            stat = os.stat(file_name)
        except OSError:
            return
        self.file_timestamp = datetime.datetime.fromtimestamp(stat[-1])
        # size in bytes
        self.file_size = stat[6]
        self._update_statistics(self.file_timestamp, self.file_size)

    def _update_statistics(self, timestamp, file_size):
        '''Summarize given stats in the stats dictionary'''
        modification_date = timestamp.strftime('%Y-%m-%d')
        if modification_date not in self.statistics:
            self.statistics[modification_date] = { 'files_count': 0, 'files_size': 0 }
        self.statistics[modification_date]['files_count'] += 1
        self.statistics[modification_date]['files_size'] += file_size

    def _find_files(self, root, files):
        '''Find files from os.walk output'''
        for item in files:
            file_name = os.path.join(root,item)
            self._get_stats(file_name)
            self._write_log(file_name, 'files')

    def _find_dirs(self, root, subFolder):
        '''Find directories from os.walk output'''
        for item in subFolder:
            dir_name = os.path.join(root,item)
            self._write_log(dir_name, 'dirs')

    def _find_all(self):
        '''Find all files/dirs in given path'''
        for root, subFolder, files in os.walk(self.conf['path'], followlinks=False):
            self._find_dirs(root, subFolder)
            self._find_files(root, files)

    def _print_statistics(self, data):
        '''Print statistics from data source'''
        denominator = 1024 * 1024 * 1024
        total_count = 0
        total_size = 0
        for date in data:
            message = "date:{}\tcount:{}\tsize:{:.2f}".format(date,
                                                              data[date]['files_count'],
                                                              data[date]['files_size'] / denominator)
            total_count += data[date]['files_count']
            total_size += data[date]['files_size']
            self._write_log(message, 'stats')
        message = "path:{} total_count:{:,} total_size: {:.2f}\n".format(self.conf['path'], total_count, total_size / denominator)
        self._write_log(message, 'stats')

    def _make_mounths_stats(self):
        '''Create per month stats from given stats'''
        self.months_stats = dict()
        for date in self.statistics:
            key = date[0:7]
            if key not in self.months_stats:
                self.months_stats[key] = { 'files_count': 0, 'files_size':0 }
            self.months_stats[key]['files_count'] += self.statistics[date]['files_count']
            self.months_stats[key]['files_size'] += self.statistics[date]['files_size']

    def run(self):
        self._parse_args()
        self._open_log()
        self._find_all()
        self._make_mounths_stats()
        self._print_statistics(self.statistics)
        self._print_statistics(self.months_stats)

if __name__ == '__main__':
    C = Find_files(args)
    C.run()

