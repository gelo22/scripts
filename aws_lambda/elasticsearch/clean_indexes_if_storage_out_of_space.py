#!/usr/bin/env python3

import urllib.request
import datetime
import json
import re
import sys

# AWS lambda script for elasticsearch log cleaning if storage have not enough free space
# lambda must have access to elasticsearch

# config with configurable values:
# min_free_space: hardcoded unit is Gb
# index_regexp: needed for index name validation and date parsing, only matched indexes will be deleted
# date_format: needed for date parsing and index sorting by this dates 
conf = dict(host = 'http://127.0.0.1',
            port = 80,
            http_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"},
            min_free_space = 1,
            index_regexp = r'^filebeat-(?P<date>\d{4}\.\d{2}.\d{2})$',
            date_format = '%Y.%m.%d'
           )

def lambda_handler(event, context):
    '''Main function, which aws will run'''
    free_space = get_free_space()
    indexes = get_indexes(conf['index_regexp'])
    oldest_index = indexes[-1]
    if free_space <= conf['min_free_space']:
        result = 'Free space is to low: {0}Gb; Removing index: {1}'.format(free_space, oldest_index)
        delete_status = delete_index(oldest_index)
        result += '; Remove operation response: {0}'.format(delete_status)
    else:
        result = 'Free space is ok: {0}Gb; Nothing to delete'.format(free_space)
    return result
    
def get_free_space():
    '''Get current free space vlue in Gb from elastic'''
    url = '{0}:{1}{2}'.format(conf['host'], conf['port'], '/_cat/allocation')
    request = urllib.request.Request(url, headers=conf['http_headers'])
    with urllib.request.urlopen(request) as resp:
        raw_free_space = resp.readline().decode('utf-8').split()[3]
    if raw_free_space.lower().endswith('gb'):
        free_space = float(raw_free_space[:-2])
    else:
        print('Error, exiting without changes, free space unit is not Gb, raw value is: {0}'.format(raw_free_space))
        sys.exit(1)
    return free_space
    
def get_indexes(index_regexp):
    '''Get available indexes matched by regexp and sort it by date from index nmae'''
    url = '{0}:{1}{2}'.format(conf['host'], conf['port'], '/_stats')
    request = urllib.request.Request(url, headers=conf['http_headers'])
    with urllib.request.urlopen(request) as resp:
        all_indexes = json.load(resp)['indices'].keys()
    regexp = re.compile(index_regexp)
    matched_indexes = list()
    for index_name in all_indexes:
        if not regexp.search(index_name):
            continue
        matched_indexes.append(index_name)
    matched_indexes.sort(key=index_to_date, reverse=True)
    return matched_indexes

def delete_index(index_name):
    '''Delete index name from elasticsearch'''
    url = '{0}:{1}/{2}'.format(conf['host'], conf['port'], index_name)
    request = urllib.request.Request(url,  headers=conf['http_headers'], method='DELETE')
    with urllib.request.urlopen(request) as resp:
        result = str(json.load(resp))
    return result
    
def index_to_date(item):
    '''Function which used for sort method, see https://docs.python.org/3/library/functions.html#sorted'''
    date_string = re.search(conf['index_regexp'], item).groupdict()['date']
    date = datetime.datetime.strptime(date_string, conf['date_format'])
    return date
    
