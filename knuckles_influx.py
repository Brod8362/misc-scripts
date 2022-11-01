#!/bin/python3
import csv
import sys
import re
from influxdb import InfluxDBClient

if len(sys.argv) != 1:
	print("usage: knuckles_influx.py < input.csv")
	quit()

cli = InfluxDBClient(host="192.168.8.1", port=8086)
reader = csv.reader(sys.stdin)
pattern = re.compile("\\d+ servers")

for (index, row) in enumerate(reader):
	author_id = row[0]
	timestamp = row[1]
	content = row[2]
	if author_id != "188453877438218240":
		res = pattern.search(content)
		if res != None:
			m = res.group(0)
			count, _ = m.split(' ')
			t = int(float(timestamp))
			influx_row = f"guild_count,bot=knuckles value={count} {t}"
			print(index)
			cli.write_points(influx_row, database="discord", time_precision="s", protocol="line")

