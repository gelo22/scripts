example:

<pre>
./smart_exec.py --la_max="0.7" --command="find /" 
</pre>

this example will run command "find /" and will pause this command's process number if LA more than "--la_max" value

will unpause it when LA lower than "--la_max"

pause = send signal STOP to process

unpause = send signal CONT to process

<pre>
usage: smart_exec.py [-h] --la_max LA_MAX [--sleep_interval SLEEP_INTERVAL]
                     --command COMMAND [--debug] [--no_renice] [--nice NICE]
                     [--ionice IONICE] [--log_file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --la_max LA_MAX       max allowed LA for system, if current LA >= la_max,
                        then command execution will be paused
  --sleep_interval SLEEP_INTERVAL
                        interrupt command execution with this interval in
                        seconds, even if other stop checks allow execution
                        (0.5 is minimal allowed value)
  --command COMMAND     command which will be executed by this script, group
                        of commands with pipes is not allowed
  --debug               enable debug mode - print debug messages to stdout
  --no_renice           disable renice mode for subprocess, because by default
                        subprocess will be reniced to lowest priority nice=19
                        ionice=3
  --nice NICE           nice value for subprocess
  --ionice IONICE       ionice value for subprocess
  --log_file LOG_FILE   set log file for subprocess output, by default print
                        to stdout
</pre>
