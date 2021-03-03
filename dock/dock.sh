#!/bin/sh
#This script runs when inserted into the dock

notify-send "Docked"

nmcli r wifi off
bluetoothctl power on 

swaymsg output eDP-1 disable
swaymsg output "Ancor Communications Inc ASUS PA238 C4LMTF095975" pos 0 0 res 1920x1080
swaymsg output "Samsung Electric Company SyncMaster HVCZ401844" pos 1920 0 res 1920x1080
