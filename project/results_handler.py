import os
import datetime as dt
from datetime import datetime
import webbrowser


def date_to_str(date):
	"""
	Convert datetime to string (04/12/2019 16:41)
	"""
	# Correct for timezone (Delft: GMT+1)
	date += dt.timedelta(hours=1)
	# Convert datetime to string
	return date.strftime("%d/%m/%Y %H:%M")

class results:
	def __init__(self, username, show_name = ""):
		self.filename = ""
		# Open webpage template
		self.webpage = open("results/templates/feed.html", "r+", encoding="utf8").read()
		self.username = username
		# Get the "most beautiful" user name, to show in the webpage
		self.show_name = username if show_name == "" else show_name
		self.saved = False

	def add_tweets(self, tweets, r_type, n):
		"""
		Add tweets to a webpage
		"""
		order_type = "influence" if tweets[0].order_by_influence else "date"
		html = ""
		if r_type == "feed":
			# Insert username where appropriate
			self.webpage = self.webpage.replace("{username}", self.show_name)
			self.webpage = self.webpage.replace("{orderf}", order_type)
			to_replace = "feed_tweets"
		else:
			self.webpage = self.webpage.replace("{orderl}", order_type)
			to_replace = "latest_tweets"
		for tweet in tweets[0:n]:
			# Recompute the global influence score by averaging tweet and news
			tweet.influence_score = (tweet.tweet_score + tweet.news_score) / 2
			# Get action type (Tweet, Retweet, Like or Reply)
			a_type = tweet.action_type()
			# Get number of replies, or show that none were scraped
			rep = "∅" if tweet.rep == -1 else f"{tweet.rep:,}"
			# Create tweet link
			tweet_link = f"https://twitter.com/i/web/status/{tweet.id}"
			if r_type == "feed":
				# Create account link
				account_link = f"https://twitter.com/{tweet.username}"
				# Check if account was a verified account
				v = " (verified)" if tweet.from_verified else ""
				title = f"""
					<h2><a target='_blank' href='{tweet_link}'>{a_type}</a> from 
					<a target='_blank' href='{account_link}'>{tweet.username}</a>{v} 
					<span>({date_to_str(tweet.date)})</span>:</h2>"""
			else:
				title = f"""
					<h2>{a_type} <span>({date_to_str(tweet.date)})</span>, 
					<a target='_blank' href='{tweet_link}'>link</a>:</h2>"""
			html += f"""
				<article>
					{title}
					<p>{tweet.text}</p>
					<i>{tweet.like:,} ❤ {tweet.rt:,} 🔁 {rep} 💬</i>
					<b>Reach score: {round(tweet.influence_score,1)}% ({round(tweet.tweet_score, 1)}% T + {round(tweet.news_score, 1)}% N)</b>
				</article>
			"""
		self.webpage = self.webpage.replace(f"{{{to_replace}}}", html)

	def save(self):
		"""
		Save the webpage on the disk
		"""
		# Create result file name, combining the current time and the username
		result_file = f"results/real/{self.username}-{datetime.now().timestamp()}.html"
		f = open(result_file, "w+", encoding="utf8")
		f.write(self.webpage)
		# Save the real path of the file (as on the computer)
		self.filename = os.path.realpath(result_file)

	def show(self):
		"""
		Open the webpage in a browser
		"""
		# Check that the results were saved on the disk first
		if not self.saved:
			self.save()
		webbrowser.open_new_tab('file://' + self.filename)
		print("Results opened in your default browser")