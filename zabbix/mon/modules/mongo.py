#!/usr/bin/env python

import json
import sys
from pymongo import MongoClient
from core.base_module import Base_check

# self.sender_data - dictionary for send
# self.conf        - dictionary with configuration
class Check(Base_check):

    def __init__(self):
       #self.client = MongoClient('mongodb://' + self.conf['host'])
        self.client = MongoClient('mongodb://' + '127.0.0.1')

    def _get_status(self):
        '''Get server statistics'''
        self.config = self.client['config']
        self.status = status = self.config.command('serverStatus')
        if status['ok']:
            pass

        self.sender_data['mongo_version'] = status['version']
        self.sender_data['uptime'] = status['uptime']
        #self.sender_data['globalLock_totalTime'] = status['globalLock']['totalTime']
        #self.sender_data['globalLock_lockTime'] = status['globalLock']['lockTime']
        self.sender_data['globalLock_currentQueue_total'] = status['globalLock']['currentQueue']['total']
        self.sender_data['globalLock_currentQueue_readers'] = status['globalLock']['currentQueue']['readers']
        self.sender_data['globalLock_currentQueue_writers'] = status['globalLock']['currentQueue']['writers']
        self.sender_data['mem_bits'] = status['mem']['bits']
        self.sender_data['mem_resident'] = status['mem']['resident']
        self.sender_data['mem_virtual'] = status['mem']['virtual']
        self.sender_data['connections_current'] = status['connections']['current']
        self.sender_data['connections_available'] = status['connections']['available']
        self.sender_data['extra_info_heap_usage'] = float("{0:.2f}".format(int(status['extra_info']['heap_usage_bytes']) / (1024*124)))
        self.sender_data['extra_info_page_faults'] = status['extra_info']['page_faults']
        #self.sender_data['indexCounters_btree_accesses'] = status['indexCounters']['btree']['accesses']
        #self.sender_data['indexCounters_btree_hits'] = status['indexCounters']['btree']['hits']
        #self.sender_data['indexCounters_btree_misses'] = status['indexCounters']['btree']['misses']
        #self.sender_data['indexCounters_btree_resets'] = status['indexCounters']['btree']['resets']
        #self.sender_data['indexCounters_btree_missRatio'] = status['indexCounters']['btree']['missRatio']
        #self.sender_data['backgroundFlushing_flushes'] = status['backgroundFlushing']['flushes']
    #no#self.sender_data['backgroundFlushing_total_ms'] = status['backgroundFlushing']['total_ms']
    #no#self.sender_data['backgroundFlushing_average_ms'] = status['backgroundFlushing']['average_ms']
    #no#self.sender_data['backgroundFlushing_last_ms'] = status['backgroundFlushing']['last_ms']
    #no#self.sender_data['cursors_totalOpen'] = status['cursors']['totalOpen']
    #no#self.sender_data['cursors_clientCursors_size'] = status['cursors']['clientCursors_size']
    #no#self.sender_data['cursors_timedOut'] = status['cursors']['timedOut']
        self.sender_data['opcounters_insert'] = status['opcounters']['insert']
        self.sender_data['opcounters_query'] = status['opcounters']['query']
        self.sender_data['opcounters_update'] = status['opcounters']['update']
        self.sender_data['opcounters_delete'] = status['opcounters']['delete']
        self.sender_data['opcounters_getmore'] = status['opcounters']['getmore']
        self.sender_data['opcounters_command'] = status['opcounters']['command']
        self.sender_data['asserts_regular'] = status['asserts']['regular']
        self.sender_data['asserts_warning'] = status['asserts']['warning']
        self.sender_data['asserts_msg'] = status['asserts']['msg']
        self.sender_data['asserts_user'] = status['asserts']['user']
        self.sender_data['asserts_rollovers'] = status['asserts']['rollovers']
        self.sender_data['network_inbound_traffic_mb'] = int(status['network']['bytesIn']) / (1024*1024)
        self.sender_data['network_outbound_traffic_mb'] = int(status['network']['bytesOut']) / (1024*1024)
        self.sender_data['network_requests'] = status['network']['numRequests']
        self.sender_data['write_backs_queued'] = status['writeBacksQueued']
    #no#self.sender_data['logging_commits'] = status['dur']['commits']
    #no#self.sender_data['logging_journal_writes_mb'] = status['dur']['journaledMB']
    #no#self.sender_data['logging_datafile_writes_mb'] = status['dur']['writeToDataFilesMB']
    #no#self.sender_data['logging_commits_in_writelock'] = status['dur']['commitsInWriteLock']
    #no#self.sender_data['logging_early_commits'] = status['dur']['earlyCommits']
    #no#self.sender_data['logging_log_buffer_prep_time_ms'] = status['dur']['timeMs']['prepLogBuffer']
    #no#self.sender_data['logging_journal_write_time_ms'] = status['dur']['timeMs']['writeToJournal']
    #no#self.sender_data['logging_datafile_write_time_ms'] = status['dur']['timeMs']['writeToDataFiles']

   #def _get_status(self):
   #    '''Get DB list and cumulative DB info'''
   #    self.admin = self.client['admin']
   #    self.db_list = db_list = self.admin.command('listDatabases')

   #    self.sender_data['db_count'] = len(db_list['databases'])
   #    self.sender_data['totalSize'] = float("{0:.2f}".format(db_list['totalSize'] / (1024*124)))

    def run(self):
        self._get_conf()
        self._get_status()
       #self._()
        self._send()

if __name__ == '__main__':
    C = Check()
    C.run()

