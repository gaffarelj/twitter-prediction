from project import cache as TC
import numpy as np
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"	# Mute TF warnings
import tensorflow as tf
import re
import json
from collections import Counter
import sys


# Adapted from https://www.tensorflow.org/tutorials/text/text_generation

batch_size, buffer_size = 1, 100000 # Buffer size defines the "shuffleness" of the dataset
char2idx, idx2char = None, None		# Dict and array containing the index corresponding to each character
checkpoint_dir = "project/data/training_checkpoints/"	# Directory were the model is saved
char_based = False

def generate_text(start, tweets=[], epochs=1, n_chars=350, train_again=False, temperature = 1.0, char_base=True):
	"""
	Generate some new text, based on what the RNN has learned from all previous tweets
	Low temperatures results in more predictable text. (high = more surprising)
	"""
	global char_based
	global checkpoint_dir
	char_based = char_base
	a = "" if train_again else "shared/"
	if char_base:
		checkpoint_dir += a + "chars"
	else:
		checkpoint_dir += a + "words"
	text = []
	# If train_again is True...
	if train_again:
		# Train a new model on new tweets, for a specified number of epochs
		model = train_model(tweets, epochs)
	# Otherwise, use an already trained model to make new predictions
	else:
		# Get latest checkpoints
		latest = tf.train.latest_checkpoint(checkpoint_dir)
		# Get the char/idx list and dict from the saved file
		open_char_idx()
		# Create empty model
		model = create_model(len(idx2char))
		# Load the previously saved weights
		try:
			model.load_weights(latest)
		except (AttributeError, ValueError):
			print("*** WARNING: no model was trained or model corrupted. Please train a new one ***")
			sys.exit()
	
	# Get the char/idx list and dict from the saved file
	open_char_idx()
	# Reset the states of the model (not the weights)
	model.reset_states()
	# Convert the start input to a list of ints (using the char/idx list)
	input_eval = []
	# For each character in the starting string, add the corresponding index if it exists
	start_l = start
	if not char_based:
		start_l = start.split()
	for s in start_l:
		try:
			input_eval.append(char2idx[s])
		except KeyError:
			print(f"WARNING: --{s}-- character was not in the training dataset")
	input_eval = tf.expand_dims(input_eval, 0)
	# For each character, predict the next one
	for i in range(n_chars):
		predictions = model(input_eval)
		# Remove the batch dimension
		predictions = tf.squeeze(predictions, 0)
		# Use a categorical distribution to predict the word returned by the model
		predictions = predictions / temperature
		predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
		# Use predicted char as next input
		input_eval = tf.expand_dims([predicted_id], 0)
		try:
			if char_based:
				text.append(idx2char[predicted_id])
			else:
				text.append(idx2char[str(predicted_id)])
		except (IndexError, KeyError):
			print(f"WARNING: --{predicted_id}-- ID does not correspond to anything in the training dataset")
	sep = "" if char_based else " "
	return (start + sep.join(text))

def train_model(tweets, epochs):
	"""
	Train the model with new tweets for a given number of epochs
	"""
	# Assemble the text from all tweets
	text = get_text(tweets)
	# Build the dataset from the text of the tweets
	dataset, vocab_size, text_arr = build_dataset(text)
	# Save the char/idx dict and list
	save_char_idx()
	# Create a new model with the given vocabulary list (number of chars)
	model = create_model(vocab_size)
	# Save all training checkpoints
	checkpoint_callback = make_checkpoints()
	# Train the model for a given number of epochs, saving all epochs on the disk
	history = model.fit(dataset, epochs=epochs, callbacks=[checkpoint_callback])
	return model

def create_model(vocab_size):
	"""
	Create a TF model, based on how many characters were used in the text vocabulary
	"""
	def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
		"""
		Build the actual TF model
		"""
		model = tf.keras.Sequential([
			tf.keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape=[batch_size, None]),
			tf.keras.layers.GRU(rnn_units, return_sequences=True, stateful=True, recurrent_initializer='random_normal_initializer'),
			tf.keras.layers.Dense(vocab_size)
		])
		return model

	def loss(labels, logits):
		"""
		Define the loss function, used by the model to know if it's doing good or not
		"""
		return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

	f = 2/3
	# Length of the embedding dimension and number of RNN units
	embedding_dim, rnn_units = int(256*f), int(1024*f)
	# Build the model
	model = build_model(vocab_size, embedding_dim, rnn_units, batch_size)
	# Compile the model
	model.compile(optimizer='adam', loss=loss)
	return model

def make_checkpoints():
	"""
	Create the checkpoint callbacks for the model
	"""
	# Checkpoints files names
	checkpoint_prefix = os.path.join(checkpoint_dir, "tf_text_ckpt_{epoch}")
	return tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_prefix, save_weights_only=True)

def save_char_idx():
	"""
	Save the char/idx list and dict on the disk
	"""
	# Open the char-idx file on the disk, erasing its previous content
	with open(checkpoint_dir + "/char-idx.txt", "w+") as f:
		# Create JSON dumps of the dict and np.ndarray (as a list), joined by the special ~ character
		if char_based:
			w = json.dumps(char2idx) + "~" + json.dumps(idx2char.tolist())
		else:
			w = json.dumps(char2idx) + "~" + json.dumps(idx2char)
		# Write the JSON dumps on the disk
		f.write(w)
	
def open_char_idx():
	"""
	Open the char/idx list and dict from the disk
	"""
	global char2idx
	global idx2char
	# Open the char-idx file on the disk, on read-only
	try:
		with open(checkpoint_dir + "/char-idx.txt", "r+") as f:
			# Read the file contents, and split at the special character ~
			t = f.read().split("~")
			# Convert JSON dumps back to a dict and a np array
			char2idx = json.loads(t[0])
			if char_based:
				idx2char = np.array(json.loads(t[1]))
			else:
				idx2char = json.loads(t[1])
	except FileNotFoundError:
		print("*** WARNING: no model was trained. Please first train one ***")
		sys.exit()

def build_dataset(text):
	"""
	Convert text to array of numbers
	"""	
	def split_input_target(chunk):
		"""
		'Translate' chars by one index.
		In word James, J (input) should be followed by a (target)
		"""
		input_text = chunk[:-1]
		target_text = chunk[1:]
		return input_text, target_text
	global idx2char
	global char2idx
	if char_based:
		# Extract unique characters from the text
		vocab = sorted(set(text))
		# Map unique characters to indices
		char2idx = {u:i for i, u in enumerate(vocab)}
		idx2char = np.array(vocab)
	else:
		text = text.split()
		word_counts = Counter(text)
		vocab = sorted(word_counts, key=word_counts.get, reverse=True)
		idx2char = {k:w for k, w in enumerate(vocab)}
		char2idx = {w:k for k, w in idx2char.items()}
	# Convert the text to array of characters indices
	text_arr = np.array([char2idx[c] for c in text])

	# Create training text
	text_train = tf.data.Dataset.from_tensor_slices(text_arr)
	n = 100
	# Convert training text to sequences
	sequences = text_train.batch(n+1, drop_remainder=True)
	# Create dataset using map function (one char should be followed by the next in generation)
	dataset = sequences.map(split_input_target)
	# Shuffle the dataset
	dataset = dataset.shuffle(buffer_size).batch(batch_size, drop_remainder=True)
	return dataset, len(vocab), text_arr

def get_text(tweets):
	"""
	Assemble the text from all tweets
	"""
	text = ""
	# Go trough all tweets
	for tweet in tweets:
		# Remove the links, @username and # from the tweet text
		tw_text = clean_text(tweet.text)
		# Append the texts togethers, with spacing
		text += tw_text + " "
	return text

def clean_text(text):
	"""
	Clean the text of the tweet
	"""
	# Replace every single space by two (helps match multiple @username one after another)
	text = text.replace(" ", "  ")
	# Add spacing before and after the text
	text = f" {text} "
	# Remove the links using a ReGex
	urlRemoval = r" ?(https?:\/\/.+?) "
	# Same for RT
	RTRemoval = r"RT  @[a-zA-Z0-9_]+: ?"
	# Same for @
	atRemoval = r" ?(@.+?) "
	# Same for #
	hashtageRemoval = r" ?(#.+?) "
	# Same for multiple dots
	dotsRemoval = r"\.{2,}"
	a = text
	# Apply the ReGexes
	text = re.sub(RTRemoval, " ", text)
	text = re.sub(urlRemoval, " ", text)
	text = re.sub(atRemoval, " ", text)
	text = re.sub(hashtageRemoval, " ", text)
	text = re.sub(dotsRemoval, " ", text)
	# Remove last …
	text = text.replace("…", " ")
	# Remove &amp;
	text = text.replace("&amp;", "and")
	# Replace multiple spaces by only one
	text = re.sub(r" {2,}", " ", text)
	# Replace text by an empty string if it is not ascii, as emoji are hardly learned by the RNN anyway
	try:
		text = text.encode("ascii").decode("ascii")
	except (UnicodeEncodeError, UnicodeDecodeError):
		text = ""
	# Make sure the text is not all CAPS
	if text == text.capitalize():
		text = text.lower()
	# Strip the text and return it
	return text.strip()
