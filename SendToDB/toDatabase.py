import redis
import pika

r = redis.StrictRedis(host='localhost', port=6379, db=0)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='toDB')

def callback(ch, method, properties, body):
    sentiment = body[:3]
    print(" [x] Received %r" % body)
    print("Sentiment:", sentiment)
    print("New Body:", body[3:])
    percentage = body[3:]
    send(sentiment, percentage)

def send(sentiment, percentage):
    sentiment = sentiment.decode()
    percentage = percentage.decode()
    r.set(sentiment, percentage)

channel.basic_consume(callback,
                      queue='toDB',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
