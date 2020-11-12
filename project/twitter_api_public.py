import requests
import json
from bs4 import BeautifulSoup
import datetime
import time


def down_json(url):
	"""
	Get json from Twitter api url
	"""
	# Download url and extract text
	req = requests.get(url).text
	# JSONP to JSON: extract content in the ()
	try:
		content = req.split("(", 1)[1].strip(")")[:-2]
	except IndexError:
		return ""
	# Load result in JSON parser
	data = json.loads(content)
	return data

def n_from_string(s):
	"""
	Extract a number from a string.
	e.g.: "21.4K Hello World" -> 21400
	"""
	# Remove useless text after the number
	n_text = s.split(" ")[0].strip()
	if len(n_text) == 0:
		return 0
	# If result is ready to be an int, return it
	if n_text[-1].isdigit():
		return int(n_text.replace(",", ""))
	# If last char is "K": multiply by a thousand
	elif n_text[-1] == "K":
		return int(float(n_text[:-1]) * 1e3)
	# If last char is "M": multiply by a million
	elif n_text[-1] == "M":
		return int(float(n_text[:-1]) * 1e6)
	return 0

def tweets_infos(tweet_ids):
	"""
	This function return the number of replies and likes of a list of tweets.
	"""
	# Join the tweet ids as one parameter
	ids_param = "-t%2C".join(tweet_ids) + "-t"
	# Tweets infos API bypass url
	url = "https://cdn.syndication.twimg.com/tweets.json?callback=__twttr.callbacks.cb0&ids=" \
		+ ids_param + "&lang=en"
	# Get JSON from url
	data = down_json(url)
	if data == "":
		print("*** WARNING: public API returned empty result, retrying in 15 secs... ***")
		time.sleep(15)
		return tweets_infos(tweet_ids)
	infos = []
	# Go trough the html of each tweet
	for id, html in data.items():
		# Parse the HTML of the timeline
		try:
			html = BeautifulSoup(html, 'html.parser')
		except TypeError:
			return -1, -1
		# Extract html of number of Replies and Likes of the tweet 
		html_R = html.find("div", {"class": "CallToAction-text"}).getText()
		html_L = html.find("span", {"class": "TweetInfo-heartStat"}).getText()
		# Extract number from html
		n_R, n_L = n_from_string(html_R), n_from_string(html_L)
		infos.append((n_R, n_L))
	return infos