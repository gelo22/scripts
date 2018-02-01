#!/bin/bash

USAGE="$0 ZABBIX_USER_NAME"

if [ ! $1 ]
    then ZABBIX_USER=zabbix
    else ZABBIX_USER=$1
fi

ID=`id -u $ZABBIX_USER`

if [ -z $ID ]
    then echo -e "No zabbix user, please provide some via:\n$USAGE"; exit 1
fi

# chmod all files to 640 and chown to root:${zabbix_user}
for f in `find /etc/zabbix/scripts/mon/ -type f`; do chown root:${ZABBIX_USER} $f; chmod 640 $f; done
# chmod all python files to 750 and chown to root:${zabbix_user}
for f in `find /etc/zabbix/scripts/mon/ -type f -name '*.py'`; do chown root:${ZABBIX_USER} $f; chmod 750 $f; done
# chmod all directories to 750 and chown to root:${zabbix_user}
for f in `find /etc/zabbix/scripts/mon/ -type d`; do chown root:{ZABBIX_USER} $f; chmod 750 $f; done
# remove compilled python code
for f in `find /etc/zabbix/scripts/mon/ -type d -name '*.pyc'`; do rm -f $f; done
#
chmod $0 u+x

