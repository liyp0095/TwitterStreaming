#!/usr/bin/python
import socket
import sys
import requests
import requests_oauthlib
import json

ACCESS_TOKEN = '1106801120796643329-YLY4KmVIZKcXw5NzsT3IVpxRzXFzgC'
ACCESS_SECRET = 'V2R9zMPRvjQGHECcxSWcIO2D3f2shcn4o02kEHIPKyCdV'
CONSUMER_KEY = 'TJZ3Tezb6AEFCDtI85BjzpDZC'
CONSUMER_SECRET = '9i4vWQGOx5gBr7iPDsPMPg1WbQ0fXMLxVGk3RqZ1KBqZ5vSAfN'
my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_SECRET)

def getTweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'), ('locations', '-122.75,36.8,-121.75,37.8,-74,40,-73,41'),('track','#')]
    # query_data = [('locations', '-90,-20,100,50'), ('track', '#')]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response

def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            tweet_text = full_tweet['text'].encode('utf-8', errors = 'ignore' ) + '\n'   # pyspark can't accept stream, add '\n'

            print("Tweet Text: " + tweet_text)
            print ("------------------------------------------")
            tcp_connection.send(tweet_text)
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)

TCP_IP = "localhost"
TCP_PORT = 9090
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected. getting tweets.")
resp = getTweets()
send_tweets_to_spark(resp,conn)
