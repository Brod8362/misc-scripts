#!/bin/sh
#This script runs when removed from the dock

notify-send "Undocked"

#networking
nmcli r wifi on
#bluetoothctl power off

swaymsg output eDP-1 pos 0 0 res 1920x1080
swamsg output DP-5 disable
swaymsg output DP-4 disable
