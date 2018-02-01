#!/usr/bin/env python

# python3 compat code
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import argparse
import os
import traceback
import datetime

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('--list', required=True, help='list of target files')
parser.add_argument('--start_position', default=0, type=int, help='start position - in bytes')
parser.add_argument('--no_error_logs', default=0, action='store_const', const=True, help='do not log errors')
parser.add_argument('--log_file', default='./' + sys.argv[0].split('/')[-1] + '.log', help='write log to file "name" or stdout if --log_file=stdout specified')
parser.add_argument('--log_interval', default=1, type=int, help='log only every N action to log file')
parser.add_argument('--files_counter', default=0, type=int, help='init value for counter of processed files')
parser.add_argument('--stop_files_counter', type=int, help='script will stop if current files_counter >= stop_files_counter')
parser.add_argument('--delete_before_this_date', default=False, help='script will delete file if its modification date is older then date: YYYY-MM-DD_hh:mm:ss')
parser.add_argument('--check', action='store_const', const=True, help='just print, skip any actions except logging, you can combine it with --log_file=stdout')
parser.add_argument('--debug', action='store_const', const=True, help='enable debug mode')
args = parser.parse_args()

class Remove_many_files:
    '''Remove files from list, where file_name pr line in list-file'''
    def __init__(self, args):
        pass

    def _parse_args(self):
        '''Add parsed arguments to "self.conf" dictionary'''
        self.conf = dict()
        for key in vars(args):
            self.conf[key] = vars(args)[key] 
        if self.conf['debug']:
            print(self.conf)

    def _open_log(self):
        '''Open log files if not stdout logging'''
        if self.conf['log_file'] == 'stdout':
            return
        self.log_file = open(self.conf['log_file'], 'a')
        self.error_log_file = open(self.conf['log_file'] + '.err', 'a')

    def _write_log(self, message):
        '''Write regular message to log, which destination depends from parsed option'''
        if self.conf['check']:
            state = 'not_removed'
        else:
            state = 'removed'
        final_message = "{} date:{} current_position:{} next_position:{} state:{}\n".format(message, self.file_timestamp, self.current_file_position, self.next_file_position, state)
        if self.conf['files_counter'] % self.conf['log_interval'] != 0:
            return
        if self.conf['log_file'] == 'stdout':
            print(final_message, end='')
            return
        self.log_file.write(final_message)
        self.log_file.flush()

    def _write_error_log(self, message):
        '''Write error message to log, which destination depends from parsed option'''
        if self.conf['no_error_logs']:
            return
        final_message = "{} current_position:{}\n".format(message, self.current_file_position)
        if self.conf['log_file'] == 'stdout':
            print(final_message, end='')
            return
        self.error_log_file.write(final_message)
        self.error_log_file.flush()

    def _write_end_log(self, message):
        '''Write last message to log which needed for last position and processed file info'''
        if not self.next_file_position:
            final_message = 'no files for delete\n'
        else:
            final_message = "{} date:{} current_position:{} next_position:{} state:this_is_last_processed_file\n".format(message, self.file_timestamp, self.current_file_position, self.next_file_position)
        if self.conf['log_file'] == 'stdout':
            print(final_message, end='')
            return
        self.log_file.write(final_message)

    def _open_list_of_files(self):
        '''Open file with list of target file_names'''
        self.list_of_files = open(self.conf['list'], 'r')

    def _get_stats(self, file_name):
        '''Get stats for file_name - size, modification time'''
        try:
            stat = os.stat(file_name)
        except OSError:
            trace = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            self._write_error_log(trace)
            self.conf['files_counter'] += 1
            return False
        self.file_timestamp = datetime.datetime.fromtimestamp(stat[-1])
        # size in bytes
        self.file_size = stat[6]
        return True

    def _after_this_date(self, string_date, file_timestamp):
        '''Check if file_name modification time is younger than "string_date", if so - then True'''
        date_limit = datetime.datetime.strptime(string_date, '%Y-%m-%d_%H:%M:%S')
        if file_timestamp > date_limit:
            return True
        else:
            return False

    def _remove_file(self, file_name):
        '''Remove file with file_name where file_name is absolute or relative path'''
        try:
            self.conf['files_counter'] += 1
            if self.conf['check']:
                self._write_log(file_name)
                return
            os.remove(file_name)
            self._write_log(file_name)
        except OSError:
            trace = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            self._write_error_log(trace)
        except KeyboardInterrupt:
            sys.exit()

    def _remove_list_of_files(self):
        '''Loop with main excludes and data collection logic'''
        self.next_file_position = False
        self.file_name = 'None'
        if self.conf['start_position']:
            self.list_of_files.seek(self.conf['start_position'])
        while True:
            self.current_file_position = self.list_of_files.tell()
            self.file_name_old = self.file_name
            self.file_name = self.list_of_files.readline().rstrip()
            # break if end of list
            if not self.file_name:
                self._write_end_log(self.file_name_old)
                break
            # skip if can't get stats for file_name
            if not self._get_stats(self.file_name):
                continue
            # skip if date is after limit
            if self.conf['delete_before_this_date'] and self._after_this_date(self.conf['delete_before_this_date'], self.file_timestamp):
                continue
            # break if limied by options
            if self.conf['stop_files_counter'] and self.conf['files_counter'] >= self.conf['stop_files_counter']:
                self._write_end_log(self.file_name_old)
                break
            self.next_file_position = self.list_of_files.tell()
            self._remove_file(self.file_name)

    def run(self):
        '''Run all things together'''
        self._parse_args()
        self._open_log()
        self._open_list_of_files()
        self._remove_list_of_files()
            
if __name__ == '__main__':
    # Initialize class and push parsed args to class
    C = Remove_many_files(args)
    C.run()

