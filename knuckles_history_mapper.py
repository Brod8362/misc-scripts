#!/bin/python3
import csv
import sys
import re
import datetime

if len(sys.argv) != 3:
	print("usage: knuckles_history_mapper.py input_file.csv output_file.csv")
	quit()

with open(sys.argv[1], 'r') as ifd:
	with open(sys.argv[2], "w") as ofd:
		reader = csv.reader(ifd)
		writer = csv.writer(ofd)
		writer.writerow(["timestamp", "servers"])
		pattern = re.compile("\\d+ servers")
		for row in reader:
			author_id = row[0]
			timestamp = row[1]
			content = row[2]
			if author_id == "712487801463242812":
				res = pattern.search(content)
				if res != None:
					m = res.group(0)
					count, _ = m.split(' ')
					t = datetime.datetime.fromtimestamp(float(timestamp))
					writer.writerow([t.strftime("%Y-%m-%d %H:%M:%S"), count])
