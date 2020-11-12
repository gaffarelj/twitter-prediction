from project import results_handler as RH
from project import News_api as NA
from project import News_weights as NW

def normalise_scores(tweets):
	"""
	Normalise the influence scores of a list by deviding each score by the maximum one
	"""
	# Set the minimum maximum as 1, to avoid division by 0
	max_tweet_score, max_news_score = 1, 1
	# Go trough every tweet and get the maximum scores
	for tweet in tweets:
		max_tweet_score = max(tweet.tweet_score, max_tweet_score)
		max_news_score = max(tweet.news_score, max_news_score)
	# Divide each score by the max, and multiply by 100 to make percentages
	for tweet in tweets:
		tweet.tweet_score *= 100/max_tweet_score
		tweet.news_score *= 100/max_news_score
	return tweets

class actions:
	"""
	Actions class: store what the last actions (tweets, likes, replies, RTs) of a specified user were
	"""
	def __init__(self, username, tweets=[]):
		self.username = username
		self.tweets = tweets

	def __str__(self):
		return f"Twitter's latest actions of {self.username} contain {len(self.tweets)} tweets."

	def add_actions(self, new_actions):
		# Use += instead of append -> allow to add multiple items at once while keeping the list flat
		if type(new_actions) == list:
			self.tweets += new_actions
		else:
			self.tweets += new_actions.tweets

	def remove_action(self, action):
		if action in self.tweets:
			self.tweets.remove(action)

	def sort(self):
		self.tweets.sort()

	def __iter__(self):
		return iter(self.tweets)

	def __len__(self):
		return len(self.tweets)

	def __lt__(self, other):
		# A list of actions is defined as lower than an other one if its most recent action is earlier than the other
		if len(other) == 0:
			return False
		elif len(self) == 0:
			return True
		return max(self.tweets) < max(other.tweets)

	def add_to_results(self, result_file):
		# Open the results webpage
		webpage = open(result_file, "r+", encoding="utf8").read()
		print(webpage)

	def __getitem__(self, item):
		# This allows to get feed item(s) by index(es): feed[3:25]
		return self.tweets[item]


class feed:
	"""
	Feed class: store what the feed of a user should be when he opens twitter
	"""
	def __init__(self, username, feed_actions = [], show_name="", feed_tweets=[]):
		self.username = username
		self.show_name = show_name
		# The feed actions are not ordered; it's a list of actions from all of his following
		self.feed_actions = feed_actions
		# The feed tweets are ordered
		self.feed_tweets = feed_tweets

	def add(self, actions):
		# Sort actions before inserting
		actions.sort()
		self.feed_actions.append(actions)

	def construct_feed(self):
		if len(self.feed_tweets) != 0:
			self.feed_tweets.sort()
			self.feed_tweets.reverse()
		else:
			l = self.len_actions()
			# Remove actions one by one, to put them in the "tweet feed"
			while self.len_actions() != 0:
				progress = (l - self.len_actions()+1)/l
				print(f"Constructing feed... {round(progress*100, 1)}%", end="\r")
				# Get the latest actions list (contains latest tweet)
				max_actions = max(self.feed_actions)
				# Get latest tweet
				latest = max(max_actions)
				# Remove latest tweet from latest action
				max_actions.remove_action(latest)
				# Add latest tweet to the tweet feed
				self.feed_tweets.append(latest)
			print()

	def __str__(self):
		return f"{self.username} followings recently made {self.len_actions()} actions."

	def __iter__(self):
		return iter(self.feed_tweets)

	def __len__(self):
		return sum([len(a) for a in self.feed_tweets])

	def len_actions(self):
		# Warning: this is not the same as __len__ as it allows to get the length of 
		# all of the actions, before they are ordered into a tweet feed
		return sum([len(a) for a in self.feed_actions])

	def __getitem__(self, item):
		# This allows to get feed item(s) by index(es): feed[3:25]
		return self.feed_tweets[item]

	def sort(self):
		self.feed_tweets.sort()

	@staticmethod
	def flag_interact(feed_ts, latest_ts):
		"""
		Set interacted=True for tweets for wich James interacted (replied to, liked, retweeted)
		"""
		# Extract list of tweet ids from the latest_tweets dict
		l_ids = [t.id for d, t in latest_ts.items()]
		# Go trough all tweets from the feed dict
		for d, f_tweet in feed_ts.items():
			# If the id of the tweet in the feed in also in the latest_tweets IDs list...
			if f_tweet.id in l_ids:
				# ... flag the tweet as "interacted"
				f_tweet.interacted = True

class tweet:
	# Tweet class: stores informations about a tweet
	def __init__(self, id, like, rt, rep, username, date, text, verif, is_rep, is_rt, order_by_influence, liked_by=None, influence_score=None, include_news=False):
		self.id = id				# Tweet ID
		self.like = like			# Number of likes
		self.rt = rt				# Number of RTs
		self.rep = rep				# Number of replies
		self.username = username	# Username that tweeted this
		self.date = date			# Date of the tweet; datetime format
		self.text = text			# Text of the tweet (might be truncated)
		self.from_verified = verif	# Was the username verified ? (boolean)
		self.is_reply = is_rep		# Is this tweet a reply to another one? (boolean)
		self.is_retweet = is_rt		# Is this tweet a RT? (boolean)
		self.liked_by = liked_by	# Username that liked this tweet (string or None)
		if influence_score is None:
			self.influence_score = self.compute_influence(include_news)
		else:
			self.influence_score = influence_score
		self.tweet_score = 0
		self.news_score = 0
		self.order_by_influence = order_by_influence
		self.interacted = False

	def __str__(self):
		v = ""
		if self.from_verified:
			v = " (verified)"
		s = f"{self.username}{v} on {self.date}:"
		s += f"\n * text: {self.text}"
		s += f"\n * got {self.like} likes, {self.rt} RTs and {self.rep} replies."
		if self.is_reply:
			s += "\n * this was a REPLY"
		if self.is_retweet:
			s += "\n * this was a RT"
		if self.liked_by is not None:
			s += "\n * liked by " + self.liked_by
		if self.influence_score is not None:
			s += f"\n * influence score of {self.influence_score}"
		return s

	def action_type(self):
		if self.is_reply:
			return "Reply"
		elif self.liked_by is not None:
			return f"Like"
		elif self.is_retweet:
			return "Retweet"
		return "Tweet"

	def __repr__(self):
		return f"tweet object (id {self.id})"

	def __lt__(self, other):
		# This allow to get the latest tweet, by comparing the dates or influence scores
		if self.order_by_influence:
			# Make sure the influence scores are still up-to-date
			self.influence_score = (self.news_score + self.tweet_score) / 2
			other.influence_score = (other.news_score + other.tweet_score) / 2
			return self.influence_score > other.influence_score
		return self.date > other.date

	def compute_influence(self, include_news=True, include_google=False):
		# Weight of each component is specified here
		likes_weight, retweets_weight, replies_weight = 5.84 / 1000, 1 / 1000, 4.28 / 1000
		weighted_likes, weighted_retweets, weighted_replies = \
			self.like * likes_weight, self.rt * retweets_weight, self.rep * replies_weight
		self.tweet_score = (weighted_likes + weighted_replies + weighted_retweets)
		self.news_score = 0
		if include_news:
			self.computer_news_influence(include_google)
		self.influence_score = round(self.tweet_score + self.news_score, 3)
		return self.influence_score

	def computer_news_influence(self, include_google):
		total_weight = 0
		engines = ["b", "g"] if include_google else ["b"]
		for engine in engines:
			search_url = NA.News_Search_URL_Builder(self.text, engine, 20)
			results = NA.News_Search(search_url)
			for i in range(1, len(results)+1):
				# Compute a ranking weight based on how far the result was on Google search
				google_rank_weight = (i+10)/i/11
				news_site = results[i-1][1]
				news_weight = NW.call(news_site, engine)
				if news_weight is not None:
					total_weight += google_rank_weight * news_weight
		self.news_score = total_weight/len(engines)
