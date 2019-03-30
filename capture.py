#!/usr/bin/env python3
# capture.py

# import RPi.GPIO as GPIO
from captureKeys import APIKey, APISecretKey, AccessKey, AccessSecretKey
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
from datetime import datetime
from pprint import pprint
import time, argparse, os, json
import pika, sys, tweepy
import pymongo
from bson import json_util

'''# setup pins
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
    time.sleep(3)'''

class listener(StreamListener):
    def other_init(self, ip):
        self.ip = ip
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")

        self.Squires = self.client["Squires"]
        self.food = self.Squires["Food"]
        self.meetings = self.Squires["Meetings"]
        self.rooms = self.Squires["Rooms"]

        self.Goodwin = self.client["Goodwin"]
        self.classrooms = self.Goodwin["Classrooms"]
        self.auditorium = self.Goodwin["Auditorium"]

        self.Library = self.client["Library"]
        self.noise = self.Library["Noise"]
        self.seating = self.Library["Seating"]
        self.wishes = self.Library["Wishes"]

    def on_data(self, data):

        data = json.loads(data)
        tweet = data["text"] # I am assuming this is a string...

        # Checkpoint 01 - Display the Command w/ current timestamp
        print("[Checkpoint 01", datetime.utcfromtimestamp(time.time()),
              "] Tweet captured: ", tweet)

        # We are inferring that the tweet format is
        # #ECE4564TXX _:_____+_____ "..."
        # ^           ^             ^
        # tag,        msg_route,    msg
        tag, msg_route, msg = tweet.split(" ",2) # splits on space

        # _:_____+_____
        # ^ ^
        # a,p_s
        action, place_subject = msg_route.split(":")

        # _____+_____
        # ^     ^
        # place,subject

        place, subject = place_subject.split("+")

        # #ECE4564TXX
        #          ^
        #          team_num
        team_num = tag[-2:] # Grab the last two chars for the team number


        storage_time = str(time.time())

        db = self.client[place]
        collection = db[subject]
        collection.insert_one({
            "Action": action,
            "Place": place,
            "MsgID": team_num + "$" + storage_time,
            "Subject": subject,
            "Message": msg
        })

        # Checkpoint 02 - Save to MongoDB via NoSQL
        print("[Checkpoint 02", datetime.utcfromtimestamp(time.time()),
              "] Stored command in MongoDB instance: ")
        document = collection.find_one({"MsgID": team_num + "$" + storage_time})
        pprint(document)

        # Checkpoint 03 - Change LED
        print("[Checkpoint 03", datetime.utcfromtimestamp(time.time()),
              "] GPIO LED: ") # TO DO: i don't know what else goes here

        '''if action == "p":
                setLEDR()
        else if action == "c":
                setLEDG()

        # Set LED back to white to show we are waiting for another command
        setLEDW()'''

        # now send this message to our message queue
        sendMessageToQueue(self.ip, document)


def sendMessageToQueue(ip, document):

    json_doc = json.dumps(document,default=json_util.default)
    json_doc = json.loads(json_doc)

    action = json_doc["Action"]
    place = json_doc["Place"]
    subject = json_doc["Subject"]
    message = json_doc["Message"]

    credentials = pika.PlainCredentials('pi', 'raspberry')
    connection = pika.BlockingConnection(
                    pika.ConnectionParameters(ip,
                                               5672, # default port
                                               '/', # default virtual host
                                               credentials))
    channel = connection.channel()

    # this sets up the exchange only if it doesn't already exist
    channel.exchange_declare(exchange=place,
                             exchange_type='direct',
                             durable=True)

    if action == "p":
        # publish this particular message to the provided exchange
        channel.basic_publish(exchange=place,
                              routing_key=subject,
                              body=message)
        # Checkpoint 04 - RabbitMQ producer success
        print("[Checkpoint 04", datetime.utcfromtimestamp(time.time()),
              "] Print out RabbitMQ command sent to the Repository RPi:",
              "\nProducer Message:",
              "\nPlace: ", place,
              "\nSubject: ", subject,
              "\nMessage: ", message)

    elif action == "c":
        print("CONSUME")
    else:
        print("WTF")
    connection.close()

    print("[Checkpoint 00", datetime.utcfromtimestamp(time.time()),
              "] Waiting for new Tweets")

def main(args):

    ip = args.server_ip
    tag = args.hashtag

    # sendMessageToQueue(ip)
    print("[Checkpoint 00", datetime.utcfromtimestamp(time.time()),
              "] Waiting for new Tweets containing", tag)

    #setLEDW()

    # setup access to Twitter API
    auth = OAuthHandler(APIKey, APISecretKey)
    auth.set_access_token(AccessKey, AccessSecretKey)

    api = tweepy.API(auth)

    myListener = listener()
    myListener.other_init(ip)

    twitterStream = Stream(auth, myListener)
    twitterStream.filter(track=[tag])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Finds tweets from API and sends to recipient')

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
