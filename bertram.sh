#!/bin/bash


for i in `ls -rt syslog*`; do
	conn_init=`zgrep -m 1 -e "openvpn.*Bertram_Lorenz.*Connection Initiated" $i | head -1`
	timeout=`zgrep -e "openvpn.*Bertram_Lorenz.*Inactivity timeout" $i | tail -1`
	if [ "$conn_init" != "" ]; then
		date=`echo $conn_init | cut -d" " -f1,2`
		login=`echo $conn_init | cut -d" " -f3`
		logout=`echo $timeout | cut -d" " -f3`
		echo "$date: $login - $logout"
	fi
done



