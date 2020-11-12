import hashlib
from datetime import datetime
import json
import glob
from project import tw_elements as TE
import re
import numpy as np
import sys


class cache:
	def __init__(self, status=0, username="", before_date=datetime.now()):
		# Status can be:
		# 0: Not active
		# 1: Write only
		# 2: Read first file before specified date (default: now), or write if not in cache
		self.write = (status == 1)
		self.read = (status == 2)
		self.before_date = before_date
		self.username = username

	def save_results(self, result):
		"""
		Save results on the drive, to be accessed later without having to re-download them
		"""
		# Detect if the results are a feed or a actions type (list of tweets)
		if type(result) == TE.feed:
			r_type = "feed"
			tweets = result.feed_tweets
		else:
			r_type = "latest"
			tweets = result.tweets
		# Create path and filename of where to save the file
		# File name containts the username, the type of result, and the current date (timestamp)
		filename = f"project/cache/{self.username}-{r_type}-{datetime.now().timestamp()}.json"
		f = open(filename, "w+", encoding="utf8")
		# Start the json list
		r = "["
		# Go trough all tweets of the feed/actions
		for tw in tweets:
			# Save each tweet object (class) as a json dump
			r += json.dumps(tw.__dict__, indent=4, sort_keys=True, default=str) + ",\n"
		# Remove the last "," from the list, and close it
		r = r[:-2] + "]"
		# Write the list of json tweets in the file
		f.writelines(r)

	def json_to_tweet(self, json_tweet, order_by_influence):
		"""
		Convert JSON tweet (from disk) back to tweet object (from tw_elements module)
		"""
		json_tweet["date"] = json_tweet["date"][:-3]+json_tweet["date"][-2:] #Date preformatting so datetime.striptime doesn't get upset
		
		return TE.tweet(json_tweet["id"], json_tweet["like"], json_tweet["rt"], json_tweet["rep"], \
			json_tweet["username"], datetime.strptime(json_tweet["date"], "%Y-%m-%d %H:%M:%S%z"), \
			json_tweet["text"], json_tweet["from_verified"], json_tweet["is_reply"], json_tweet["is_retweet"], \
			order_by_influence, json_tweet["liked_by"], json_tweet["influence_score"])

	def get_cached(self, r_type, order_by_influence=True):
		"""
		Return latest feed or actions from the cache
		"""
		# Get all json content corresponding to the specified pathname/filename pattern
		files = self.get_json_files(f"project/cache/{self.username}-{r_type}*")
		# Return False (and an empty string) if no files could be found
		if len(files) == 0:
			return False, ""
		# Get the latest date from the keys of the json content dict 
		first_bf_date = self.first_before_date(r_type)
		# Get the json of the latest file in the dict
		last_file = files[first_bf_date]
		tweets = []
		# Go trough every tweet in the json content of the file
		for t in last_file:
			# Reconstruct a tweet object from the json data
			tweet = self.json_to_tweet(t, order_by_influence)
			add_even_if_self_tweeted = False
			if not(tweet.username.lower() == self.username and r_type == "feed") or add_even_if_self_tweeted:
				# Add the tweet object to the list of tweets constituing the feed/actions
				tweets.append(tweet)
		print(f"Getting {r_type} of {self.username} from cache ({self.before_date.strftime('%d/%m/%Y %H:%M')})")
		if r_type == "feed":
			# If the results are a feed, return true, and a feed object containing all of the tweets
			return True, TE.feed(self.username, feed_tweets=tweets)
		elif r_type == "latest":
			# If the results are actions, return true, and an actions object containing all of the tweets
			return True, TE.actions(self.username, tweets=tweets)

	def get_json_files(self, f_name):
		"""
		Get all json content from files in a folder in a dict (keys are dates)
		"""
		files = dict()
		# Go trough all files corresponding to the f_name pathname pattern (example: cache/elonmusk-feed*.json)
		for f_name in glob.glob(f_name):
			# Extract timestamp from filename
			date = re.search("-([0-9]+\.[0-9]+)\.json", f_name).group(1)
			# Convert timestamp back to datetime format
			date = datetime.fromtimestamp(int(date.split(".")[0]))
			# Read the file content
			try:
				with open(f_name, "r+", encoding="utf-8") as f:
					f_json = json.loads(f.read())
					# Put the json-decoded content in the dict
					files[date] = f_json
			except:
				print(f_name)
				print("*** Warning: error in JSON decoding of the above file ***")
				sys.exit()
		return files

	def available_dates(self, do_print=True, r_type="latest"):
		"""
		Print at which dates the cache has data for the specified username
		"""
		# Get all files in cache concerning the specified username
		files = self.get_json_files(f"project/cache/{self.username}-{r_type}*")
		if not do_print:
			return files.keys()
		# Inform user if there is no cache for that username
		if len(files) == 0:
			print(f"There is no data in cache for {self.username}")
		else:
			# Print date at which objects for that username have been cached. Dates are the dict keys of the cached files
			print(f"Dates at wich data ({r_type}) of {self.username} has been cached:")
			# Also print index, might make this function allow the user to enter the index to select a date (TODO?)
			for i, (d, v) in enumerate(files.items()):
				print(f"  {i}:  {d}, {len(v)} tweets")

	def first_before_date(self, r_type):
		"""
		Return the first available date in the cache, before the one specified in __init__
		"""
		# Get all dates in cache
		dates = list(self.available_dates(False, r_type))
		# Sort the dates list
		dates.sort()
		# Reverse the dates list to have the newest one first
		dates = dates[::-1]
		# Go trough all the dates
		for date in dates:
			# When a date is finally before the specified one, return it
			if date < self.before_date:
				return date

	@staticmethod
	def split_latest_feed(latests, feed, n=50):
		"""
		Returns the latest tweets (as dict keys) with the n tweets that were before in the feed (as dict values)
		(Return dict with keys = one latest tweet, value = list of n tweets before the latest tweet)
		"""
		r = dict()
		# Get the dates of every tweet in the feed dict (they are the keys)
		feed_dates = list(feed.keys())
		# Go trough every tweet of the latest dict
		for t_date, latest_tweet in latests.items():
			# Get the indices of the n tweets from the feed that were tweeted right before James' tweet
			before_latest = np.where(np.array(feed_dates) < t_date)[-1][-n:-1]
			# Save the n tweets, from their indices, in a dict
			r[latest_tweet] = [feed[feed_dates[d]] for d in before_latest]
		return r

	def get_all_cached(self):
		"""
		Return all cached results for specified username
		"""
		latest = dict()
		feed = dict()
		# Get all files in the cache folder that start with the given username
		files = self.get_json_files(f"project/cache/{self.username}-*")
		if len(files) == 0:
			print("*** WARNING: the specified username couldn't be found in the cache ***")
			return None, None
		# Go trough every file (dates are the keys of the dict)
		for i, (date, file) in enumerate(files.items()):
			print(f"Getting all from cache from {self.username}... ({i+1}/{len(files)})", end="\r")
			r_type = "latest"
			# If the file contain more than 50 tweets, it's a feed (latest tweets otherwise)
			if len(file) > 50:
				r_type = "feed"
			# Go through every tweet in the file
			for t in file:
				# Convert the JSON tweet back to a tweet object
				tweet = self.json_to_tweet(t, False)
				# Save tweet in appropriate dict (key: tweet id, value: tweet) if its not already in it
				if r_type == "latest" and not (tweet.id in latest.keys()):
					latest[tweet.id] = tweet
				elif not (tweet.id in feed.keys()):
					feed[tweet.id] = tweet
		print()
		# Convert the dict to lists
		latest, feed = list(latest.values()), list(feed.values())
		# Sort the lists (by tweet date)
		latest.sort(), feed.sort()
		# Convert the lists back to dict (key: tweet date, value: tweet)
		latest, feed = {l.date:l for l in latest}, {f.date:f for f in feed}
		return latest, feed
