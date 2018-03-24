import re
import tweepy
from textblob import TextBlob
from tweepy import OAuthHandler
import pika
import time


class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'edRRnahlbuww2zI9zdWDmReTm'
        consumer_secret = 'NUCSZ3vrtgjs296hvBcjHyYesP7tTIgAbEZPhuvYSzet9FkmYa'
        access_token = '558457723-AzxjUXHmrGeqczCKWrBGyWzvXuraCD7N8Gc69qS1'
        access_token_secret = 'Sa0iq3rWqdMgdEF3gd0KVFJKJz94OoDd4jG3MqRvZzKfm'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split()))

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []
        # call twitter api to fetch tweets
        fetched_tweets = self.api.search(q=query, count=count)

        # parsing tweets one by one
        for tweet in fetched_tweets:
            # empty dictionary to store required params of a tweet
            parsed_tweet = {}
            # tweet.decode("utf-8")
            # saving text of tweet
            parsed_tweet['text'] = tweet.text
            # parsed_tweet['text'].decode("utf-8")
            # saving sentiment of tweet

            #parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

            # parsed_tweet['sentiment'].decode()
            # appending parsed tweet to tweets list
            if tweet.retweet_count > 0:
                # if tweet has retweets, ensure that it is appended only once
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
                    sendInPikaChannel(str(parsed_tweet))
            else:
                tweets.append(parsed_tweet)
                sendInPikaChannel(str(parsed_tweet))
        # return parsed tweets
            """return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))"""

def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    while True:
        api.get_tweets(query='Donald Trump', count=200)
        #sendInPikaChannel(tweets)
        time.sleep(60)
        # toDatabase.send(positive_tweet_percentage, negative_tweet_percentage, neutral_tweet_percentage)
        # toDatabase.retrieve()

def sendInPikaChannel(tweet):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='sendTweets')
    channel.basic_publish(exchange='',
                          routing_key='sendTweets',
                          body=tweet)
    print("Sent: ", tweet)
    channel.close()
    connection.close()

if __name__ == "__main__":
    # calling main function
    main()