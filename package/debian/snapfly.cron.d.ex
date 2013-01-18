#
# Regular cron jobs for the snapfly package
#
0 4	* * *	root	[ -x /usr/bin/snapfly_maintenance ] && /usr/bin/snapfly_maintenance
