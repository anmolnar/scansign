#!/usr/bin/python

import argparse
import re
import gzip
from datetime import datetime, timedelta
import os.path, time

parser = argparse.ArgumentParser(description='OpenVPN usage statistics')
parser.add_argument('logfile', type=str, help='OpenVPN logfile (syslog format)')
parser.add_argument('username', type=str, help='Name of the user to create usage statistics')

args = parser.parse_args()

login_pattern = re.compile("^([A-Z][a-z]{{2}} +\d{{1,2}} \d+:\d+:\d+).*openvpn.*\[{username}\].*Connection Initiated".format(username = args.username))
logout_pattern = re.compile("^([A-Z][a-z]{{2}} +\d{{1,2}} \d+:\d+:\d+).*openvpn.*\[{username}\].*Inactivity timeout".format(username = args.username))

if args.logfile.endswith("gz"):
	log = gzip.open(args.logfile, 'rb')
else:
	log = open(args.logfile, 'r')

user_logins = dict()
user_logouts = dict()

file_time = time.localtime(os.path.getmtime(args.logfile))

for line in log:
	login = login_pattern.search(line)		
	if login:
		datetime_string = time.strftime('%Y', file_time) + ' ' + login.group(1)
		login_datetime = datetime.strptime(datetime_string, '%Y %b %d %H:%M:%S')
		lid = login_datetime.date()
		lit = login_datetime.time()
		if lid not in user_logins or lit < user_logins[lid].time():
			user_logins[lid] = login_datetime
	logout = logout_pattern.search(line)
	if logout:
		datetime_string = time.strftime('%Y', file_time) + ' ' + logout.group(1)
		logout_datetime = datetime.strptime(datetime_string, '%Y %b %d %H:%M:%S')
		lod = logout_datetime.date()
		lot = logout_datetime.time()
		if lod not in user_logouts or lot > user_logouts[lod].time():
			user_logouts[lod] = logout_datetime

log.close()

time_spent = dict()

for ld, lt in user_logins.iteritems():
	if ld in user_logouts:
		time_spent[ld] = user_logouts[ld] - user_logins[ld]

sum_td = timedelta()

print "{user} login - logout VPN time - {date}".format(user=args.username, date=time.strftime('%Y %B', file_time))

for ld in sorted(time_spent.keys()):
	ts = time_spent[ld]
	sum_td += ts
	total_seconds = (ts.microseconds + (ts.seconds + ts.days * 24 * 3600) * 10**6) / 10**6
	hours = total_seconds // (60*60)
	minutes = (total_seconds % (60*60)) / 60
	print "{date} - {h} hours {m:0} minutes - login: {login} - logout: {logout}".format(date=ld.strftime('%b %d'), h=hours, m=minutes, login=user_logins[ld].strftime('%H:%M'), logout=user_logouts[ld].strftime('%H:%M'))

print 'Total: {hours} hours {mins} minutes'.format(hours=(sum_td.days * 24) + sum_td.seconds / 60 / 60, mins=(sum_td.seconds % (60*60) / 60))


