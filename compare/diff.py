#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

file_1 = sys.argv[1]
file_2 = sys.argv[2]

list_1 = list()
list_2 = list()

def add_file_to_list(file_name, list_name):
    '''Add strings from file to list, eliminate dulicates, lowercase, remove edge blanks'''
    file_object = open(file_name)
    for line in file_object:
        line = line.strip().lower()
        if not line:
            continue
        if line not in list_name:
            list_name.append(line)
    list_name.sort()

def print_not_in_second(list_name_1, list_name_2, message):
    '''Print lines from first list which not in second list'''
    print(message)
    for line in list_name_1:
        if line not in list_name_2:
            print(line)

add_file_to_list(file_1, list_1)
add_file_to_list(file_2, list_2)
print_not_in_second(list_1, list_2, 'ONLY_IN_LEFT:')
print('===========+++++===========')
print_not_in_second(list_2, list_1, 'ONLY_IN_RIGHT:')

