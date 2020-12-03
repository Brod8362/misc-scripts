#!/usr/bin/python
import sys

len_str = b"\x88\x3f\xf0\x00\x00\x00\x00\x00"
with open(sys.argv[1], "r+b") as f:
	print("Opening file...")
	s = f.read()
f = open(sys.argv[1], "r+b")
print("Searching for offset")
offset = s.find(b'\x44\x89')
print(f"Found offset of {offset}")
f.seek(offset+2)
print(f"Writing to offset")
f.write(len_str)
print(f"Closing file")
f.close()
