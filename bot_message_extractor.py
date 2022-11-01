#!/bin/python3
import discord
import sys
import asyncio
import csv
import time

if len(sys.argv) != 3:
	print("\tusage:\n\t\tbot_message_extractor.py token user_id > output.csv")
	quit(1)

class DiscordClient(discord.Client):
	async def on_ready(self):
		sys.stderr.write(f"logged in as {self.user}")
		target_user_id = sys.argv[2]
		user = await self.fetch_user(target_user_id)
		count = 0
		csv_writer = csv.writer(sys.stdout)
		csv_writer.writerow(["author", "timestamp", "content"])
		async for message in user.history(limit=20000):
			csv_writer.writerow([message.author.id, time.mktime(message.created_at.timetuple()), message.content])
			count += 1
		sys.stderr.write(f"saved {count} messages")
		await self.close()
			

intents = discord.Intents.default()
client = DiscordClient(intents=intents)
client.run(sys.argv[1])
