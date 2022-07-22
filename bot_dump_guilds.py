#!/bin/python3
import discord
import sys
import json

if len(sys.argv) != 3:
	print("\tusage:\n\t\tbot_dump_guilds.py token file.json")
	quit(1)

class DiscordClient(discord.Client):
	async def on_ready(self):
		sys.stderr.write(f"logged in as {self.user}")
		js = []
		with open(sys.argv[2], "w") as fd:
			async for g in self.fetch_guilds(limit=1000):
				obj = {
					"id": g.id,
					"name": g.name,
				}
				js.append(obj)
			json.dump(js, fd, indent=4)
		exit(0)

intents = discord.Intents.default()
client = DiscordClient(intents=intents)
client.run(sys.argv[1])
