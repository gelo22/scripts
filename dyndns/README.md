### Purpose:

Script which able to create/update DNS A-record via namesilo API https://www.namesilo.com/Support/API-Manager

### Features:

Client only need to connect to a server via ssh

scheme

<pre>
----------   ssh   ----------   ----------------
| client |-------->| server |-->| namesilo API |
----------         ----------   ----------------
</pre>

### Requirements

Server OS Linux, BSD, etc, which have open-ssh server and Python version 2 or 3
namesilo API key
client with ssh-client

### Examle:

git clone

copy code to target user home on the server
<pre>
cp -a repo_dir/* /home/my_user/
</pre>

example host name:
<pre>
example.com
</pre>

add your root dimain to ddns.py.conf
example:
<pre>
"root_domain": "example.com"
</pre>

add your hostname to ddns.py.conf
example:
<pre>
"allowed_hostnames": ["my_hostname.example.com", "my-router-home", "my-another-host", "my-etc"]
</pre>

add your host ssh key to .ssh/authorized_keys
example key:
<pre>
command="./ddns.py --host_name=my_hostname.example.com" ssh-rsa my_ssh_key #my_comment
</pre>

from the client connect to the server(my_user@my_server) via ssh
<pre>
ssh my_user@my_server
</pre>

now your DNS A-record my_hostname.example.com updated to your source ip
you able to check API response in a directory ./ddns_logs/ which contain log files


### Examle with default interface IP:

It will use default interface IP to update DNS record
Add to crontab:

<pre>
* * * * * cd && /home/ddns/ddns.py -host_name=my_hostname.example.com --address=me
</pre>

### Examle with manual IP:

It will use provided IP to update DNS record

<pre>
/home/ddns/ddns.py -host_name=my_hostname.example.com --address=11.1.1.1
</pre>
