from project import twitter_api as TAPI
from project import tw_elements as TE
from project import results_handler as RH
from project import cache as TC
import project.News_weights as Nw
from project import tf_text as TT
from project import Predictor_Network as PN
import time
from datetime import datetime


# Example with elonmusk:
name = ["elonmusk", "Elon Musk"]


inputs = [
	f"Show latest feed and tweets of {name[1]} (LIVE)",
	f"Show latest feed and tweets of {name[1]} (FROM CACHE)",
	f"Get all from the cache and build training datasets",
	f"Use Tensorflow to predict {name[1]}'s possible next Tweet",
	f"Start an infinite loop that add tweets to the cache every hour",
	f"Create the data for News readership numbers (takes a long time)",
	f"Call the predictor NN (unfortunatly unfinished)"
	]
for i, v in enumerate(inputs):
	print(f"{i+1}: {v}")
choice = None
while choice not in range(1, len(inputs)+1):
	try:
		choice = int(input(f"Please input one of the options [1-{len(inputs)}]: "))
	except ValueError:
		choice = None
print()


if choice in [1, 2]:
	cache = TC.cache(status=choice, username=name[0])
	# Get the twitter feed of the specified user, as well as his last tweets
	twitter_feed = TAPI.get_feed(name[0], cache, show_name=name[1], get_replies=False, order_by_influence=False)
	print(f"Getting {name[1]}'s last tweets...")
	last_tweets = TAPI.get_user_interactions(name[0], 0, get_replies=True, order_by_influence=True, n=20, cache=cache)
	# Sort the feed tweets and keep the one we want before normalising and computing influence score
	twitter_feed.sort()
	twitter_feed = twitter_feed[0:20]
	# Switch this to compute influence again (based on news article that might have been written since then)
	compute_influence_again = True
	if compute_influence_again:
		for i, tweet in enumerate(last_tweets):
			print(f"Computing news influence of last tweets... ({i+1}/{len(last_tweets)})", end="\r")
			tweet.compute_influence(include_news=True, include_google=False)
		print()
		for i, tweet in enumerate(twitter_feed):
			print(f"Computing news influence of feed tweets... ({i+1}/{len(twitter_feed)})", end="\r")
			tweet.compute_influence(include_news=True, include_google=False)
		print()
	last_tweets = TE.normalise_scores(last_tweets)
	twitter_feed = TE.normalise_scores(twitter_feed)
	# Sort the tweets after normalisation
	last_tweets.sort()
	# Save the results in a webpage, and open it
	res = RH.results(name[0], show_name=name[1])
	res.add_tweets(twitter_feed, "feed", n=20)
	res.add_tweets(last_tweets, "latest", n=20)
	res.show()

if choice == 3:
	# These functions should be useful to build training datasets
	cache = TC.cache(username=name[0])
	latest, feed = cache.get_all_cached()
	if (latest, feed) != (None, None):
		# Build a dict {tweet: feed just before said tweet}
		data = cache.split_latest_feed(latest, feed)
		print(len(data), len(latest), len(feed))
		# Set interacted=True for tweets for which James interacted (replied to, liked, retweeted)
		TE.feed.flag_interact(feed, latest)
		i = sum([t.interacted for d, t in feed.items()])
		print(f"{name[1]} interacted with {i} of {len(feed)} tweets in his feed")
	
if choice == 4:
	char_base = input("Base prediction on words (on characters otherwise) ? [Y/n]: ").lower() == "n"
	do_train = input("Use a pre-trained model to do the prediction (train a new one otherwise) ? [Y/n]: ").lower() == "n"
	start = input("By default (just press ENTER), predicted sentence starts with \"I have been\" \nInput a string of 2-6 words to change it: ")
	print()
	n = 280 if char_base else 50
	if len(start) < 5:
		start = "I have been "
	if do_train:
		latest, feed = TC.cache(0, username=name[0]).get_all_cached()
		tweets = list(latest.values())
		print(f"Training model based on text of {len(tweets)} tweets...")
		text = TT.generate_text(start, tweets=tweets, epochs=50, n_chars=n, train_again=do_train, char_base=char_base)
	else:
		text = TT.generate_text(start, n_chars=n, train_again=False, temperature=1.0, char_base=char_base)
	print(text)

cache_loop = TC.cache(status=1, username=name[0])
while choice == 5:
	print(datetime.now().strftime('%d/%m/%Y %H:%M'))
	t0 = time.time()
	print("Downloading new results for the cache...")
	last_tweets = TAPI.get_user_interactions(name[0], 0, get_replies=True, order_by_influence=False, cache=cache_loop)
	twitter_feed = TAPI.get_feed(name[0], cache_loop, show_name=name[1], get_replies=False, order_by_influence=False)
	print("Done, sleeping 1h")
	dt = time.time()-t0
	time.sleep(3600 - dt)

if choice == 6:
	Nw.create(True, False)

if choice == 7:
	tweet_list = TC.cache.get_all_cached(cache_loop)
	PN.create_model(tweet_list, tweet_list, train=True, predict=True)
