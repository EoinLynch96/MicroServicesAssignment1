import redis
import pika

r = redis.StrictRedis(host='localhost', port=6379, db=0)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='fromDB')

def retriveInformation(sentiment):
    percentage = r.get(sentiment)
    sendInPikaChannel(sentiment, percentage)

def sendInPikaChannel(sentiment, tweet_percentage):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='fromDB')
    channel.basic_publish(exchange='',
                          routing_key='fromDB',
                          #body = positive_tweet_percentage + negative_tweet_percentage + neutral_tweet_percentage)
                          body = sentiment + str(tweet_percentage))
    print("Sent Information")
    connection.close()

retriveInformation('pos')
retriveInformation('neg')
retriveInformation('neu')
