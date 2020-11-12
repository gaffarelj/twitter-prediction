import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from requests_oauthlib import OAuth1
import time
from project import tw_elements as TE
from project import twitter_api_public as TAPIP
from project import cache as TC
import sys


# Twitter DEV API keys
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

def extract_twitter_time(date):
	"""
	Extract the datetime from a str, using Twitter's format
	"""
	try:
		return datetime.strptime(date, "%a %b %d %H:%M:%S %z %Y")
	except ValueError:
		return None

def extract_tweet_infos(tweet):
	"""
	Extract specific tweet infos, from the JSON reply of the API
	"""
	id = tweet["id_str"]
	date = extract_twitter_time(tweet["created_at"])
	text = tweet["full_text"].replace("\n", " ").strip() # Might need some decoding
	username = tweet["user"]["screen_name"]
	verif = bool(tweet["user"]["verified"])
	rt = int(tweet["retweet_count"])
	like = int(tweet["favorite_count"])
	# Check if the tweet was a reply
	is_rep = tweet["in_reply_to_status_id"] is not None
	# Check if the tweet was a retweet
	is_rt = "retweeted_status" in tweet.keys()
	return id, username, like, rt, date, text, verif, is_rep, is_rt

def dev_api_request(url):
	"""
	Call the DEV API at a given URL
	"""
	read_ok = False
	# Create OAuth headers, following OAuth1 protocol
	oauth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret, signature_type="query")
	# Request API url
	resp = requests.get(url, auth=oauth)
	# Extract API rate limite remaining from the headers
	req_limit = int(resp.headers["x-rate-limit-remaining"])
	# If there is less than 7 requests left in the interval, slow the code down
	if req_limit < 10:
		if req_limit < 7:
			# Get interval reset time
			req_reset = int(resp.headers["x-rate-limit-reset"])
			# Compute time the code must sleep by taking a quarter of the time left before interval reset
			sleep_time = (req_reset - time.time()) / 4
			print()
			print(f"Waiting {round(sleep_time, 1)} seconds to stay below the API rate limit. You might want to stop and try again in 5mins.")
			print()
			time.sleep(sleep_time)
		else:
			# Warn user of the numbers of API calls left in the interval
			print()
			print(f"*** WARNING: only {req_limit} API calls left in this interval ***")
			print()
	resp_json = resp.json()
	return resp_json

def get_user_following(username):
	"""
	Using the DEV API, get the name of all of the accounts followed by username
	"""
	# Declare API url, including the username
	api_url = f"https://api.twitter.com/1.1/friends/list.json?screen_name={username}&count=200&skip_status=true&include_user_entities=false"
	# Get API response
	resp_json = dev_api_request(api_url)
	# Get names from response
	users = []
	try:
		for user in resp_json["users"]:
			users.append(user["screen_name"])
	except KeyError:
		print("*** WARNING: user couldn't be found on Twitter ***")
		sys.exit()
	return users

def get_tweet(id):
	"""
	Using the DEV API, get number of likes, rts and replies from a tweet. As well as who tweeted it
	"""
	# Declare API url, including the tweet id
	api_url = f"https://api.twitter.com/1.1/statuses/show.json?id={id}"
	# Get API response
	resp_json = dev_api_request(api_url)
	# Extract tweet infos from JSON
	id, username, like, rt, date, text, verif, is_rep, is_rt = extract_tweet_infos(resp_json)
	rep = -1
	return TE.tweet(id, like, rt, rep, username, date, text, verif, is_rep, is_rt)

def get_user_interactions(username, type, order_by_influence, get_replies=False, n=20, n_l=10, cache=TC.cache(0)):
	"""
	Get the last n tweets/RTs/replies (type 0), only tweets(type 1), or likes (type 2) of a user
	"""
	exist = False
	if cache.read:
		exist, latest = cache.get_cached("latest", order_by_influence)
		if exist:
			return latest
		else:
			print("User interactions couldn't be found in the cache, trying live...")
	TL = []
	# Make sure the specified number is not too high
	n = min(n, 150)
	liked_by = None
	# Type 0: get tweets, rts and replies
	if type == 0:
		# Declare API url, including the username and the specified number of tweets/RTs/replies to get
		api_url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={username}&count={n}&include_rts=1&tweet_mode=extended"
	# Type 1: only get tweets
	elif type == 1:
		api_url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={username}&count={n}&include_rts=0&exclude_replies=true&tweet_mode=extended"
	# Type 2: get likes
	elif type == 2:
		api_url = f"https://api.twitter.com/1.1/favorites/list.json?screen_name={username}&count={n_l}&tweet_mode=extended"
		liked_by = username
	else:
		return TL
	# Get API response
	resp_json = dev_api_request(api_url)
	# Check if number of tweets/RTs returned by the API matches the specified one
	count = len(resp_json)
	if count == 1 and type != 2:
		print(f"\n*** WARNING: only got 1 tweet instead of the {n} requested. Retrying in 15secs...***\n")
		time.sleep(15)
		return get_user_interactions(username, type, order_by_influence, get_replies, n, n_l, cache)
	TWs = []
	ids = []
	# Go trough each tweet...
	for tweet in resp_json:
		# Extract tweet infos from JSON
		try:
			id, username, like, rt, date, text, verif, is_rep, is_rt = extract_tweet_infos(tweet)
		except TypeError:
			print("\n*** WARNING: the API response was not in the correct format... Retrying in 15secs... ***\n")
			time.sleep(15)
			return get_user_interactions(username, type, order_by_influence, get_replies, n, n_l, cache)
		# Save tweet id in a list to later get replies number
		ids.append(id)
		TWs.append((id, username, like, rt, date, text, verif, is_rep, is_rt))
	replies_likes = []
	# If replies number are also to be scraped, use the public API
	if get_replies:
		replies_likes = TAPIP.tweets_infos(ids)
	# Go trough all Tweets informations
	for i, TW in enumerate(TWs):
		id, username, like, rt, date, text, verif, is_rep, is_rt = TW
		try:
			rep = replies_likes[i][0]
		except IndexError:
			rep = -1
		# Save the tweet as a Tweet object
		TL.append(TE.tweet(id, like, rt, rep, username, date, text, verif, is_rep, is_rt, order_by_influence, liked_by))
	interactions = TE.actions(username, [])
	interactions.add_actions(TL)
	if cache.write or (cache.read and not exist):
		cache.save_results(interactions)
	return interactions

def get_actions(username, order_by_influence, get_replies=False, cache=TC.cache(0)):
	"""
	Get all likes, tweets, retweets and replies of a specified user
	"""
	# Create actions object
	actions = TE.actions(username, [])
	# Add tweets/RTs/replies to actions
	actions.add_actions(get_user_interactions(username, 0, order_by_influence, get_replies=get_replies, cache=cache))
	# Add likes to actions
	actions.add_actions(get_user_interactions(username, 2, order_by_influence, cache=cache))
	return actions

def get_feed(username, cache=TC.cache(0), show_name="", get_replies=False, order_by_influence=False):
	"""
	Get the Twitter feed that the specified username should see when he opens Twitter
	"""
	exist = False
	if cache.read:
		exist, feed = cache.get_cached("feed", order_by_influence)
		if exist:
			feed.construct_feed()
			return feed
		else:
			print("User feed couldn't be found in the cache, trying live...")
	# Get the followings of the specified username
	followings = get_user_following(username)
	# Create feed object
	feed = TE.feed(username, show_name=show_name)
	# For each following...
	for i, following in enumerate(followings):
		print(f"Getting latest actions of {len(followings)} twitter accounts... ({i+1}/{len(followings)})", end="\r")
		# Get latest actions (likes, tweets, replies, RTs)
		f_actions = get_actions(following, order_by_influence, get_replies=get_replies)
		feed.add(f_actions)
	print()
	# Construct the feed by picking the latest actions ones by ones
	feed.construct_feed()
	if cache.write or (cache.read and not exist):
		cache.save_results(feed)
	return feed
