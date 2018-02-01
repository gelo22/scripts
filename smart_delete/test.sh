#!/bin/bash
mkdir -p /tmp/tst/d1/d11/d111
mkdir -p /tmp/tst/d2/
touch /tmp/tst/f1
touch /tmp/tst/f2
touch /tmp/tst/d1/fd1
touch /tmp/tst/d1/d11/fd11
touch /tmp/tst/d2/fd2
find /tmp/tst/ -type f > /tmp/list
