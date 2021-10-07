#! /usr/bin/env python3

import re
import sys

# pip3 install --user pyaml


metrics_to_exclude = [
   #'# TYPE :',
    ':',
   #'# TYPE apiserver_request:',
   #'# TYPE cluster:',
   #'# TYPE code:',
   #'# TYPE code_verb:',
   #'# TYPE instance:',
   #'# TYPE namespace:',
   #'# TYPE namespace_workload_pod:',
   #'# TYPE node:',
   #'# TYPE ALERTS',
    'ALERTS',
    'up',
    ]

metrics_per_job = dict()
job_re = re.compile(r'.+,job="(?P<job>.*?)"')

tmp_data = {
    'metric_name': None,
    'state': 'find_metric',
}

def process_metrics():
    '''Process metrics'''
    with open('metrics.txt') as metrics_file:
        for line in metrics_file:
           #if exclude_line(line):
           #    continue
            process_function = globals()['process_metrics_'+ tmp_data['state']]
            process_function(line)


def exclude_line(line):
    '''Exclude not needed metrics'''
    for exclude in metrics_to_exclude:
        if line.startswith(exclude):
            return True
    if line.startswith('# TYPE ') and ':' in line:
        return True

def process_metrics_find_metric(line):
    '''Find metric in string'''
    if line.startswith('# TYPE '):
        metric_name = line.split()[2]
        for exclusion in metrics_to_exclude:
            if exclusion in metric_name:
                return
        tmp_data['metric_name'] = metric_name
       #print(tmp_data['metric_name'])
        tmp_data['state'] = 'find_job'

def process_metrics_find_job(line):
    '''Find job in metric string'''
    if tmp_data['metric_name'] and line.startswith(tmp_data['metric_name']):
        re_match = job_re.match(line)
        if not re_match:
            print('No job label in string: {}'.format(line))
            sys.exit(1)
        job = re_match.groupdict()['job']
       #print(job)
        if job not in metrics_per_job:
            metrics_per_job[job] = list()
        metrics_per_job[job].append(tmp_data['metric_name'])
        tmp_data['state'] = 'find_metric'

            
def get_rules():
    with open('rules.json') as metrics_file:
        tmp_data['rules'] = metrics_file.read()
       #for line in metrics_file:
       #    pass

def get_dashboards():
    with open('dashboards.yaml') as dashboards_file:
        tmp_data['dashboards'] = dashboards_file.read()
       #for line in dashboards_file:
       #    pass

process_metrics()
get_rules()
get_dashboards()

#import pprint
#pprint.pprint(metrics_per_job)

for job in metrics_per_job:
    metrics = metrics_per_job[job]
    metrics_set = set()
    for metric in metrics:
        if metric in tmp_data['rules'] or metric in tmp_data['dashboards']:
            metrics_set.add(metric)
    print('job: {}, regexp: ^{}$'.format(job, '$|^'.join(metrics_set)))
