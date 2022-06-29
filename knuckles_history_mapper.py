#!/bin/python3
import csv
import sys
import re
import datetime
import matplotlib.pyplot as mpl
import matplotlib.dates as mdates
import matplotlib

if len(sys.argv) != 3:
	print("usage: knuckles_history_mapper.py input_file.csv output_file.csv")
	quit()


dates = []
amount = []

with open(sys.argv[1], 'r') as ifd:
		reader = csv.reader(ifd)
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
					dates.append(datetime.datetime.fromtimestamp(float(timestamp)))
					amount.append(int(count))

dates.reverse()
amount.reverse()
for i in range(0, max(amount), 100):
	mpl.axhline(y=i, color="black", linewidth=0.25)
mpl.plot(dates, amount)
mpl.locator_params(axis='x', maxticks=24)
mpl.locator_params(axis='y', nbins=25)
year_locator = mdates.YearLocator()
month_lcoator = mdates.MonthLocator()
mpl.title("Knuckles bot growth since launch")
mpl.xlabel("Time")
mpl.ylabel("Server count")
mpl.savefig(sys.argv[2], dpi=300)
