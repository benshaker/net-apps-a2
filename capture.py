#!/usr/bin/env python3
# capture.py

# import RPi.GPIO as GPIO
import time
import argparse
import os
from captureKeys import APIKey, APISecretKey, AccessKey, AccessSecretKey
import json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import pika, sys, tweepy

# setup pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT) # Red
GPIO.setup(13, GPIO.OUT) # Green
GPIO.setup(15, GPIO.OUT) # Blue

def setLEDW(self):
        # white LED - Waiting for command
	GPIO.output(11, GPIO.HIGH)
	GPIO.output(13, GPIO.HIGH)
	GPIO.output(15, GPIO.HIGH)
	time.sleep(3)

def setLEDR(self):
        # red LED - Received pulish request
        GPIO.output(11, GPIO.HIGH)
	GPIO.output(13, GPIO.LOW)
	GPIO.output(15, GPIO.LOW)
	time.sleep(3)

def setLEDG(self):
	# green LED - Received consume request
	GPIO.output(11, GPIO.LOW)
	GPIO.output(13, GPIO.HIGH)
	GPIO.output(15, GPIO.LOW)
	time.sleep(3)

class listener(StreamListener):

        def setIP(self, ip):
                self.ip = ip

	def on_data(self, data):
		tweet = all_data["text"] # I am assuming this is a string...

                # Checkpoint 01 - Display the Command
                print("[Checkpoint 01 ", TIME) # TO BE CHANGED BY CHRISTINA

                # We are inferring that the format is #ECE4564TXX _:____+_____ "..."
		tag, command = tweet.split(" ", 2)
		team = tag[-2:] # Grab the last two chars which should be the team number 
		action, command = command.split(":", 1)
		place, command = command.split("+", 1)
		subject, message = command.split(" ", 1)

                # Checkpoint 02 - Save to MongoDB via NoSQL
                db.____.insertOne(
                        {
                               Action: action
                               Place: place
                               MsgID: team + "$" + time.time()
                               Subject: subject
                               Message: message
                        }
                )

                
                # Checkpoint 03 - Change LED
                if action == "p":
                        setLEDR()
                else if action == "c":
                        setLEDG()
                
		# Sending the message to Repo
		sendMessageToQueue(self.ip)

                # Set LED back to white to show we are waiting for another command
                setLEDW()
		

def sendMessageToQueue(ip):
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()

	channel.queue_declare(queue='hello')

	channel.basic_publish(exchange='',
						  routing_key='hello',
						  body='Hello World!')
	print(" [x] Sent 'Hello World!'")
	connection.close()
		
def main(args):
	
	ip = args.server_ip
	tag = args.hashtag

	setLEDW()
	
	# setup access to Twitter API
	auth = OAuthHandler(APIKey, APISecretKey)
	auth.set_access_token(AccessKey, AccessSecretKey)

	api = tweepy.API(auth)

	myListener = listener()
	myListener.setIP(ip)
	
	twitterStream = Stream(auth, myListener)
	twitterStream.filter(track=[tag])
	

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
