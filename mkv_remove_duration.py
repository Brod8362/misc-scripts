#!/usr/bin/python
import sys
import mmap

len_str = b"\x88\x3f\xf0\x00\x00\x00\x00\x00"
ext = sys.argv[1].split(".")[-1]
if (ext.lower() not in {"mkv","webm"}):
	print("file is not webm or mkv, exiting")
	sys.exit(1)
with open(sys.argv[1], "r+b") as f:
	mm = mmap.mmap(f.fileno(), 0)
	offset = mm.find(b'\x44\x89')
	mm.seek(offset+2)
	mm.write(len_str)
	mm.close()

