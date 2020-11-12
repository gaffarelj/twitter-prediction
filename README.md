# Twitter's influenza

How influenced and influential is someone on Twitter?

## The Project

### Introduction

This project is about analysing someone's Twitter feed. Let's call him James. Twitter's developer API is used to get his tweets and the amount of likes, replies and retweets of his tweets.
Google and Bing news search are used to get news articles about his tweets. Each news site has its own weight (based on readership numbers). 
Based on these numbers, an 'influence score' (that is perhaps better described as a 'reach score') is computed for each of his tweets.
The same logic (minus the news search) is applied for each of his following's latest tweets (they constitute his feed).

His possible next tweet's text is predicted using a Recurrent Neural Network and his previous tweets text as training data.

Finally, his next interaction is predicted using Neural Networks and previous interactions (likes, retweets, replies) as training data.


### Prerequisites

[Python version 3.7](https://www.python.org/downloads/release/python-370) is advised for TensorFlow to work without issues. Tensorflow 2.0 Alpha is preferered to Tensorflow 2.0 stable, because some functionalities were broken in the stable version (like estimation of the training model time).
The modules used in the project are:

```
numpy==1.16.5
requests
bs4
requests_oauthlib
lxml
tensorflow==2.0.0-alpha0
```

## Files and structure

### Modules description

Everything can be run from [main.py](main.py) by means of a simple command interface.

The core of the software are the [twitter_api](project/twitter_api.py) and [tw_elements](project/tw_elements.py) modules. These modules get the tweets from Twitter, and interpret the
returned JSON files. They then create custom "tweet" objects with the amount of likes, replies etc (all of the wanted information) of that tweet so that in can be used more easily
in the rest of the code.

[results_handler](project/results_handler.py) is a module that shows the results (James' latest tweets, as well as his feed) on a webpage in an easily readable way.

The [cache](project/cache.py) module stores the analysed results from the Twitter API. There is an option to, before requesting a tweet, check if it's in the cache already. Twitter having a request limit,
this helps reduce the number of similar requests that would otherwise be made. The cache also makes gathering tweets more efficient since reading a file from disk is faster than doing a request.

[News_api](project/News_api.py) is a module for searching news articles via Google and Bing and returning the influence score and basic info of each article.

[News_weights](project/News_weights) is a sub package that computes the weight of a news outlet, based on its market share and readership numbers pulled from Wikipedia. 

[tf_text](project/tf_text.py) is a Recurrent Neural Network that uses the text of James' tweets. This text is cleaned and split in either words or characters. 
By learning how the words/characters follow each other (finding recurrent patterns), it learns to predict new tweets' text. This does not necessarily lead to proper English, 
and the predicted text is sometime exactly the same as one of James' earlier tweets. However, we are confident that the output is still interesting to study, 
and that having more training tweets would help with these issues.

[Predictor_Network](project/Predictor_Network.py) is a Neural Network that analyses the tweets in the cache in an attempt to find a pattern. Its output is what James' next action would be.

### Tests

All of the unit tests can be found in the [project/test folder](project/test).

### Repository structure

Everything can be run from [main.py](main.py), and the modules are in the [project](project) folder. 

The [docs](docs) folder contains the [project report](docs/Group_14_Project.pdf) and the [presentations](docs/presentation).

The [project/cache](project/cache) folder contains the json file that are the analysed output of the Twitter API.

The [project/News_weights](project/News_weights) folder contains the News_weights package, which is used to determine the readersip numbers of News outlets.
The workflow is split into multiple files to keep an overview and to avoid too long files.
Inside there is the [data](project/News_weights/data) folder, which contains all the data files that the package uses.

The [project/data/training_checkpoints](project/data/training_checkpoints) folder contains a [shared](project/data/training_checkpoints/shared) folder with two pre-trained models, 
for characters and words based predictions. The models are saved by default in two empty folders ([chars](project/data/training_checkpoints/chars) and [words](project/data/training_checkpoints/words)), 
and these models are not synchronised on GitLab. These need to be manually added to the [shared](project/data/training_checkpoints/shared) folder.

The [results](results) folder contain a [template](results/templates/feed.html) used by the [results_handler](project/results_handler.py) to build the result webpage. 
The results webpages are saved in an [empty folder](results/real), and these webpages are not synchronised on GitLab.