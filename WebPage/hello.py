from flask import Flask, render_template
app = Flask(__name__)
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/')
def displayInformation():
    dictionary = retriveInformation()
    return render_template("hello.html", result = dictionary)

def retriveInformation():
    dictionary = {}
    sentiment_list = ['pos', 'neg', 'neu']
    for sentiment in sentiment_list:
        percentage = r.get(sentiment)
        dictionary[sentiment] = percentage.decode()
    print(dictionary)
    return dictionary

if __name__ == '__main__':
   app.run()