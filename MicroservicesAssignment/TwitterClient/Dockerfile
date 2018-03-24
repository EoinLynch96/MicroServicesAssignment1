FROM python:3.6-slim
ADD . /TwitterClient
WORKDIR /TwitterClient
RUN pip install -r requirements.txt
CMD ["python", "StreamTweets.py"]
