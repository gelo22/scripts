###Purpose:

Delete many files from list with ability to start from specific position in list

###Features:

Delete specific number of files from list

Delete files with timestamp before provided timestamp

Write logs with log interval (every N file in list)

Separate error log

Run without operations for check only

###Examle:
<pre>
I have list of files in /tmp/list, it contain absolute path in each  line
/tmp/tst/f1
/tmp/tst/d2/fd2
/tmp/tst/d1/fd1
/tmp/tst/d1/d11/fd11
/tmp/tst/f2
</pre>
next command will process files in list, print every second row of process log, print error logs, stop after two deleted files, will start from position 12 (this is second line in list), will delete files with modification/creation data before 2017-09-01_00:00:01 :
<pre>
ionice -c 3 nice -n 19 ./smart_delete.py --list=/tmp/list --stop_files_counter=2 --log_interval=2 --delete_before_this_date=2017-09-01_00:00:01 --start_position=12 --log_file=stdout
</pre>
command output:
<pre>
/tmp/tst/d1/fd1 date:2017-01-22 00:37:08 current_position:28 next_position:44 state:removed
/tmp/tst/d1/fd1 date:2017-01-22 00:37:08 current_position:44 next_position:44 state:this_is_last_processed_file
</pre>

help:
<pre>
usage: smart_delete.py [-h] --list LIST [--start_position START_POSITION]
                       [--no_error_logs] [--log_file LOG_FILE]
                       [--log_interval LOG_INTERVAL]
                       [--files_counter FILES_COUNTER]
                       [--stop_files_counter STOP_FILES_COUNTER]
                       [--delete_before_this_date DELETE_BEFORE_THIS_DATE]
                       [--check] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --list LIST           list of target files
  --start_position START_POSITION
                        start position - in bytes
  --no_error_logs       do not log errors
  --log_file LOG_FILE   write log to file "name" or stdout if
                        --log_file=stdout specified
  --log_interval LOG_INTERVAL
                        log only every N action to log file
  --files_counter FILES_COUNTER
                        init value for counter of processed files
  --stop_files_counter STOP_FILES_COUNTER
                        script will stop if current files_counter >=
                        stop_files_counter
  --delete_before_this_date DELETE_BEFORE_THIS_DATE
                        script will delete file if its modification date is
                        older then date: YYYY-MM-DD_hh:mm:ss
  --check               just print, skip any actions except logging, you can
                        combine it with --log_file=stdout
  --debug               enable debug mode
</pre>
