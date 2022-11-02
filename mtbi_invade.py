#!/bin/python3
import requests
import random
import json
import sys

def random_mbti() -> str:
	ei = random.choice(["E", "I"])
	sn = random.choice(["S", "N"])
	tf = random.choice(["T", "F"])
	jp = random.choice(["J", "P"])
	return ei+sn+tf+jp

def random_name(length: int) -> str:
	chars = list("qwertyuiopasdfghjklzxcvbnm")
	n = ""
	for i in range (0, length):
		n += random.choice(chars)
	return n

def submit(name: str, group_id: str, mbti: str = random_mbti()):
	content = {
		"memberName": name,
		"groupId": group_id,
		"mbti": mbti
	}
	resp = requests.post(
		"https://ddok9.com/api/mbti/member",
		json = content
	)
	return resp

if __name__ == "__main__":
	mbti = random_mbti()
	if len(sys.argv) < 4:
		print("missing arguments: [random|insert] code [count|name] (mbti)")
		exit(1)
	mode = sys.argv[1]
	code = sys.argv[2]
	arg3 = sys.argv[3]
	mbti = sys.argv[4] if len(sys.argv) > 4 else random_mbti()
	if mode == "random":
		try:
			count = int(arg3)
		except:
			print("cannot decide number (arg3)")
			exit(1)
		for i in range(0, count):
			name = random_name(10)
			print(name)
			r = submit(random_name(10), code, random_mbti())
			if r.status_code != 200:
				print(f"failed on index {i} ({r.status_code})")
				exit(1)
		exit(0)
	elif mode == "insert":
		r =submit(arg3, code, mbti)
		if (r.status_code == 200):
			exit(0)
		else:
			exit(1)
	else:
		print("invalid mode")
		exit(1) 	
