#!/usr/bin/env python

class Base_check:

    sender_data = dict()

    def _get_conf(self):
        '''Run config parser'''
        from mon_conf import Get_conf
        self.conf = Get_conf(self.args).run()

    def _send(self):
        '''Run zabbix sender'''
        from mon_sender import Mon_sender
        Mon_sender(self.args, self.sender_data).run()

    def _discovery(self):
        '''Run discovery'''
        from mon_discovery import Mon_discovery
        Mon_discovery(self.args, self.sender_data).run()

