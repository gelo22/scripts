This script able to execute commands on muultiple hosts via openssh and 
copy files in both directions via scp(openssh) with useful options.

It works with python2 only now and have no other dependencies.

It useful on jump servers, where employer restrict any ansible or similar soft usage.

All useful options, which you able to change via command line - presented in config file, which can be used for default values.

Example usage in ssh mode: 
```
./ssh.py SERVER(S) COMMAND [OPTIONAL_ARGS]
```
Example usage in scp mode: 
```
./ssh.py SERVER(S):/remotefile /localfile mode=scp [OPTIONAL_ARGS]
./ssh.py /localfile SERVER(S):/remotefile mode=scp [OPTIONAL_ARGS]
```
Where SERVER(S) can be: 

- host(s) - separated by comma(s) HOST,HOST,HOST:
```
./ssh.py HOST,HOST,HOST COMMAND [OPTIONAL_ARGS]
```
Next command will copy /localfile to all hosts in list:
```
./ssh.py /localfile HOST,HOST,HOST:/remotefile mode=scp [OPTIONAL_ARGS]
```
Next command will copy /localfile from all hosts in list to files /localfile_HOST
```
./ssh.py HOST,HOST,HOST:/remotefile /localfile mode=scp [OPTIONAL_ARGS]
```
- group(s) of hosts from ansible inventory (default 'hosts' file in the current directory)
```
./ssh.py GROUP,GROUP,GROUP COMMAND [OPTIONAL_ARGS]
```
- any combinations of HOSTS and GROUPS:
```
./ssh.py GROUP,HOST,GROUP,HOST COMMAND [OPTIONAL_ARGS]
```
- special HOST 'all' - will run ssh or scp on all HOSTS from ansible inventory and any hosts in list, which not in ansible inventory
```
./ssh.py all,example.com COMMAND [OPTIONAL_ARGS]
```
will execute command on all servers from ansible inventory and on example.com, any duplicates in resulting list will be ignored
no mater how many times some host occurs  (if it have the same hostname) - in the resulting list it will be only one
- python regular expression, which will select hosts from listed HOSTS and GROUPS from ansible inventory (limited to characters ^${}[]*+|()?') )
```
./ssh.py '^web.*',all 'hostname'
```
will execute command 'hostname' on all hosts, which name start from 'web'
```
./ssh.py 'web.*',some_project 'hostname'
```
will execute command 'hostname' on all hosts from group ',some_project', which name contain 'web'

You can set ssh user via more intuitive way:
```
./ssh.py user@SERVER(S) COMMAND [OPTIONAL_ARGS]
./ssh.py user@SERVER(S):/remotefile /localfile mode=scp [OPTIONAL_ARGS]
./ssh.py /localfile user@SERVER(S):/remotefile mode=scp [OPTIONAL_ARGS]
```

File 'ssh.py_config' contain all optional arguments(OPTIONAL_ARGS) and comments with explanations.

Each optional argument can be overrided by the same agrument in command line

