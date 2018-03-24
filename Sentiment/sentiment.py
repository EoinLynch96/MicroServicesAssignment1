from textblob import TextBlob
import re
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='sendTweets')
tweets = []
parsed_tweets = []

def callback(ch, method, properties, body):
    sentiment = body[:3]
    #print(" [x] Received %r" % body)
    #print("Sentiment:", sentiment)
    #print("New Body:", body[3:])
    tweet = body
    if tweet not in tweets:
        tweets.append(tweet)
    #parsed_tweets = get_parsed_tweets()
    for tweet in tweets:
        parsed_tweet = {}
        parsed_tweet['text'] = tweet
        parsed_tweet['sentiment'] = get_tweet_sentiment(str(tweet))
        #print("Sentiment: ", parsed_tweet['sentiment'])
        #print("parsed_tweet", parsed_tweet)
        parsed_tweets.append(parsed_tweet)

    ptweets = [tweet for tweet in parsed_tweets if tweet['sentiment'] == 'positive']

    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in parsed_tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Num pos tweets: ", len(ptweets))
    print("Num neg tweets: ", len(ntweets))
    print("Num total tweets: ", len(parsed_tweets))
    print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(parsed_tweets)))
    # percentage of neutral tweets
    #neutral_tweet_percentage = "{} % \ ".format(100 * len(tweets - ntweets - ptweets) / len(tweets))
    neutral_tweet_percentage = (100 * (len(tweets) - len(ntweets) - len(ptweets)) / len(parsed_tweets))
    print("Neutral tweets percentage: ", neutral_tweet_percentage)
    neutral_tweet_percentage = (100 * (len(parsed_tweets) - len(ntweets) - len(ptweets)) / len(parsed_tweets))
    #print("Neutral tweets percentage: {} % \ ".format(100 * len(tweets - ntweets - ptweets) / len(tweets)))"""
    positive_tweet_percentage = (100 * len(ptweets) / len(parsed_tweets))
    negative_tweet_percentage = (100 * len(ntweets) / len(parsed_tweets))
    #neutral_tweet_percentage = (100 * (len(tweets) - len(ntweets) - len(ptweets)) / len(tweets))
    print("Current Positive: ", positive_tweet_percentage)
    print("Current Negative: ", negative_tweet_percentage)
    print("Current Neutral: ", neutral_tweet_percentage)
    sendInPikaChannel("pos", positive_tweet_percentage)
    sendInPikaChannel("neg", negative_tweet_percentage)
    sendInPikaChannel("neu", neutral_tweet_percentage)


def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split()))


def get_tweet_sentiment(tweet):
    '''
    Utility function to classify sentiment of passed tweet
    using textblob's sentiment method
    '''
    # create TextBlob object of passed tweet text
    analysis = TextBlob(clean_tweet(tweet))
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def get_parsed_tweets():
    parsed_tweets = []
    for tweet in tweets:
        parsed_tweet = {}
        parsed_tweet['text'] = tweet
        parsed_tweet['sentiment'] = get_tweet_sentiment(str(tweet))
        parsed_tweets.append(parsed_tweet)
    return parsed_tweets

def sendInPikaChannel(sentiment, tweet_percentage):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='toDB')
    channel.basic_publish(exchange='',
                          routing_key='toDB',
                          # body = positive_tweet_percentage + negative_tweet_percentage + neutral_tweet_percentage)
                          body=sentiment + str(tweet_percentage))
    print("Sent Information")
    connection.close()

channel.basic_consume(callback,
                  queue='sendTweets',
                  no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
