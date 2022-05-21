#!/bin/bash
modprobe batman-adv
sudo pkill NetworkManager
ifconfig wlp1s0 down
iwconfig wlp1s0 mode ad-hoc 

ifconfig wlp1s0 mtu 1532
iwconfig wlp1s0 mode ad-hoc essid RED-Adhoc ap 02:1B:55:AD:0C:02  channel 1 
sleep 1
ip link set wlp1s0 up 
sleep 1
batctl if add wlp1s0
ifconfig bat0 up
ifconfig bat0 10.1.1.10
