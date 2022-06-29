#!/bin/python3
import discord
import sys
import asyncio
import csv
import time

if len(sys.argv) != 3:
	print("\tusage:\n\t\tbot_message_extractor.py token user_id")
	quit()

class DiscordClient(discord.Client):
	async def on_ready(self):
		print(f"logged in as {self.user}")
		target_user_id = sys.argv[2]
		user = await self.fetch_user(target_user_id)
		count = 0
		with open(f"messages_{user.name}.csv", "w") as fd:
			csv_writer = csv.writer(fd)
			csv_writer.writerow(["author", "timestamp", "content"])
			async for message in user.history(limit=20000):
				csv_writer.writerow([message.author.id, time.mktime(message.created_at.timetuple()), message.content])
				count += 1
		print(f"saved {count} messages")
		await self.close()
			

intents = discord.Intents.default()
client = DiscordClient(intents=intents)
client.run(sys.argv[1])
