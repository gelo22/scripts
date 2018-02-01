example:

<pre>
./smart_exec.py --la_max="0.7" --command="find /" 
</pre>

this example will run command "find /" and will pause this command's process number if LA more than "--la_max" value

will unpause it when LA lower than "--la_max"

<pre>
usage: smart_exec.py [-h] --la_max LA_MAX --command COMMAND [--debug]
                     [--debug_log_file DEBUG_LOG_FILE] [--no_renice]
                     [--nice NICE] [--ionice IONICE] [--log_file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --la_max LA_MAX       max allowed LA for system, if current LA >= la_max,
                        then command execution will be paused
  --command COMMAND     command which will be executed by this script, group
                        of commands with pipes is not allowed
  --debug               enable debug mode - print debug messages to stdout
  --debug_log_file DEBUG_LOG_FILE
                        set log file for debug output, by default print to
                        stdout
  --no_renice           disable renice mode for subprocess, because by default
                        subprocess will be reniced to lowest priority nice=19
                        ionice=3
  --nice NICE           nice value for subprocess
  --ionice IONICE       ionice value for subprocess
  --log_file LOG_FILE   set log file for subprocess output, by default print
</pre>

