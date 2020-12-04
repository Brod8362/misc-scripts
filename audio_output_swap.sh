#!/bin/bash

availableSinks=( "alsa_output.pci-0000_00_1b.0.analog-stereo" "alsa_output.usb-Logitech_G533_Gaming_Headset-00.analog-stereo" )
default=$(pacmd list-sinks | grep -A1 "*" | grep "name:" | sed "s/\tname: <//" | sed "s/>//")

function set_default() {
	pacmd set-default-sink $1
	pacmd list-sink-inputs | grep index | while read line; do
		pacmd move-sink-input `echo $line | cut -f2 -d' '` $1
	done
}

if [ $default = ${availableSinks[0]} ]; then
	set_default ${availableSinks[1]}
else
	set_default ${availableSinks[0]}
fi
