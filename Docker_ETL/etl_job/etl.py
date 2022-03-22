


import pymongo
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import re
import time
import logging  # the luxury version of print
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Connect to the docker mongo container

client =  pymongo.MongoClient("mongodb")  #initialize

###connection to docker postgres container
engine_tweet_db = create_engine('postgresql://postgres:titanic99@postgresdb:5432/tweetdb')



###connect to the database in mongo db twitter
db = client.twitter   
    

##name your tweets in collection
my_tweet_collection=list(db.tweets.find())

####save the tweets to data frame
df_record = pd.DataFrame(my_tweet_collection)

##clean the data using regular expression
mentions_regex= '@[A-Za-z0-9]+'
url_regex='https?:\/\/\S+' #this will not catch all possible URLs
hashtag_regex= '#'
rt_regex= 'RT\s'

def clean_tweets(tweet):
    tweet = re.sub(mentions_regex, '', tweet)  #removes @mentions
    tweet = re.sub(hashtag_regex, '', tweet) #removes hashtag symbol
    tweet = re.sub(rt_regex, '', tweet) #removes RT to announce retweet
    tweet = re.sub(url_regex, '', tweet) #removes most URLs
    
    return tweet

##apply the function on ur tweet dataframe
df_record.text =df_record.text.apply(clean_tweets)


##initilaize sentiment analysis
analyser = SentimentIntensityAnalyzer()

###run the sentiment anlysis oon the column with the tweets
pol_scores = df_record['text'].apply(analyser.polarity_scores).apply(pd.Series)
pol_scores.head(3)

if pol_scores.shape[0]!=0:
    logging.critical(pol_scores)
else:
    logging.critical('check bug')

###create new data frame and add compound column
df=pd.concat([df_record, pol_scores['compound']], axis=1)
df.head(3)


#modify dataframe to include only data needed in postgres
df_tweet=df[['text','compound']]


##transfer the tweet_dataframe to dabtabse( tweet) and name the table pollution_tweets
df_tweet.to_sql('pollution_tweet', engine_tweet_db )

if df_tweet.to_sql:
    logging.critical('pollution_tweet')
else:
    logging.critical('check bug')

