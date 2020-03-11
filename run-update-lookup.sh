#!/bin/sh
# Maybe run from crontab like 
# */5 * * * * /home/cisco/csm-nso-lookup-package/run-update-lookup.sh > /dev/null
# but maybe even better than this script it to use flock
# * * * * * /usr/bin/flock -n /tmp/fcj.lockfile /usr/bin/python2.7 /home/mydir/public_html/myotherdir/script.py
pid_file='/tmp/update-lookup.pid'
if [ ! -s "$pid_file" ] || ! kill -0 $(cat $pid_file) > /dev/null 2>&1; then
  echo $$ > "$pid_file"
  cd /home/cisco/csm-nso-lookup-package/
  exec python update-lookup.py --timer 10 
fi
