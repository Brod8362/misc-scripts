#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook
import re
import sys
import time

#url = "https://www.lso.cc/auction/2700/item/52-cicso-catalyst-switches-84165/"
url = sys.argv[1].strip()
webhook = "https://canary.discord.com/api/webhooks/963893655398129735/BmyCP_NQmAOQn3N4Dp6GQZcxgkn80SB0StTZ3TQH1252KSZ5ZPsfEOZ1HN_syeupynkW"
ua = "Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0"

headers = {
	'User-Agent': ua
}

opt = Options()
opt.add_argument('--headless')
opt.add_argument('--disable-gpu')

driver = webdriver.Chrome(chrome_options=opt)


prev = ""
while True:
	driver.get(url)
	time.sleep(3)
	soup = BeautifulSoup(driver.page_source, "html.parser")
	res = soup.find_all("span", {"data-currency": re.compile(r".*")})
	if len(res) > 0:
		txt = res[0].get_text()
		if txt != prev:
			wh = DiscordWebhook(url=webhook, content=f"<@188453877438218240> <@316258808026628096> price update **{txt}**\n{url}")
			wh.execute()
		prev = txt
	time.sleep(30)

driver.close()
