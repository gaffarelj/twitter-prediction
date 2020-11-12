import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D, Conv1D, MaxPool1D
from tensorflow.keras.callbacks import TensorBoard
import numpy as np
import os
import random
import time
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

'''
Using Tensorboard:
pip install tensorboard if necessary
Go to the project folder in cmd. How I did it is to open the folder in windows explorer and type in cmd into the
address bar.
Paste this :   python -m tensorboard.main --logdir=[logs/]   into cmd (don't add quotes or whatever)
Copy-Paste the localhost url into your browser
It'll give an error like "No dashboards are active for the current data set.", I don't know why this happens
'''

'''
Note: If PyCharm yells at you that it's not finding Keras, try updating to the latest version of PyCharm
Note 2: Do pip install tensorflow if you don't have tensorflow yet. This will take a while though
Name of the log file. time.time is there to ensure unique model names
'''
# NAME = f"James-twitter-predictor-{round(time.time(), 3)}"

# This weird filepath is necessary, TensorBoard will yell at you otherwise
# tensorboard = TensorBoard(log_dir=f"project\\logs\\{NAME}\\")


# Create a list which we will feed through the network
def create_data(tweet_list):
	main_data = []
# 	actions = [Tweet, Reply, Like, Retweet]
	actions = [0, 1, 2, 3]
	for tweet in tweet_list:
		for key in tweet:
			if tweet[key].action_type() == "Tweet":
				main_data.append(actions[0])
			elif tweet[key].action_type() == "Reply":
				main_data.append(actions[1])
			elif tweet[key].action_type() == "Like":
				main_data.append(actions[2])
			else:
				# tweet.action_type() == "Retweet":
				main_data.append(actions[3])

	return main_data

'''
Split data
Even list is every even index (0, 2, 4...) - This is the action
Odd list is every odd index (1, 3, 5...) - This is what happens after the action
So I want to compare an action and what he does afterwards
'''
def split_data(main_data):
	main_data = create_data(main_data)
	even_list = []
	odd_list = []
	# Make two lists of tweet objects...
	for i in range(len(main_data)):
		# 0 % 1 is also 0, so checking for that exception
		if i == 0 or i % 2 == 0:
			even_list.append(main_data[i])
		else:
			odd_list.append(main_data[i])

	# X, y is more used for recognition (so it's item, label), but I had no idea what else to put it as
	# Make sure both lists are the same length
	if len(odd_list) != len(even_list):
		idx = min(len(odd_list), len(even_list))
		odd_list, even_list = odd_list[0:idx], even_list[0:idx]
	return even_list, odd_list

# By default, we will train the model and predict
# https://www.tensorflow.org/guide/keras/train_and_evaluate

def create_model(main_data, tweet_list, train=True, predict=True):
	X, y = split_data(main_data)
	#print(X, y)
	percentage = 0.1

	# print("Lengths: ")
	# print(len(X))
	# print(len(y))

	# X, y = tweet_list

	# Keep a percentage of the data for validation (10% now)
	X_val = X[-int(len(X)*percentage):]
	y_val = y[-int(len(y)*percentage):]
	X_train = X[:-int(len(X)*percentage)]
	y_train = y[:-int(len(y)*percentage)]


	# FYI, I know that this 'test' ain't good, will fix soon


	test_sample = X[5], y[5]
	val_sample = X[5], y[5]

	# Add layers
	model = Sequential([Dense(64, activation='relu', input_shape=(1,)),
						Dense(64, activation='relu',),
						Dense(4, activation='sigmoid')])

	model.compile(loss='sparse_categorical_crossentropy',
				optimizer='adam',)
				# metrics=['accuracy'])

	# optimizer = tf.keras.optimizers.RMSprop(0.001)
	#
	# model.compile(loss='mse',
	# 			optimizer=optimizer,
	# 			metrics=['mae', 'mse'])

	prediction = "You have set predict to False, the model will not predict anything"
	validation = "This function is linked to predicting. Set predict to True"
	model.summary()

	# Epochs is how many times our data passes through the network.
	if train:
		model.fit(X_train, y_train, batch_size=1, epochs=5) #, callbacks=[tensorboard])

	if predict:
		print('\n# Generate predictions for 3 samples')
		prediction = model.predict(X_val, y_val)
		# print('predictions shape:', prediction.shape)
		print(f"predictions: {prediction}")

	return model, prediction, validation


