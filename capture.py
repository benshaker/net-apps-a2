#!/usr/bin/env python3
# capture.py

import RPi.GPIO as GPIO
import time
import argparse
import os
import captureKeys
import json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

class listener(StreamListener):

	def on_data(self, data):
		tweet = all_data["text"]
		tweet = tweet.split(" ")
		
		
		


def main(args):

	# setup pins
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(11, GPIO.OUT) # Red
	GPIO.setup(13, GPIO.OUT) # Green
	GPIO.setup(15, GPIO.OUT) # Blue

	# white LED - Waiting for command
	GPIO.output(11, GPIO.HIGH)
	GPIO.output(13, GPIO.HIGH)
	GPIO.output(15, GPIO.HIGH)
	time.sleep(3)
	
	ip = args.server_ip
	tag = args.hashtag
	
	# setup access to Twitter API
	auth = OAuthHandler(APIKey, APISecretKey)
	auth.set_access_token(AccessKey, AccessSecretKey)

	api = tweepy.API(auth)	
	
	twitterStream = Stream(auth, listener())
	twitterStream.filter(track=[args[3]])
	
	# GET https://api.twitter.com/1.1/search/user_timeline.json?q=tag

	# red LED - Received pulish request
	GPIO.output(13, GPIO.LOW)
	GPIO.output(15, GPIO.LOW)
	time.sleep(3)

	# green LED - Received consume request
	GPIO.output(11, GPIO.LOW)
	GPIO.output(13, GPIO.HIGH)
	time.sleep(3)


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Finds tweets from API and sends to reciptent')
	
	parser.add_argument('--server_ip',
						'-sip',
						'-s',
						help="The IP address of the server",
						type=str)
	
	parser.add_argument('--hashtag',
						'-t',
						help="The hashtag string to be found in the API",
						type=str)
						
	if len(sys.argv) != 5:
		print("Error: Too few arguments provided. Please see --help for more information.")
	else:
		main(parser.parse_args(sys.argv[1:]))