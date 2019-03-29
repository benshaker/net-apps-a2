#!/usr/bin/env python3
# capture.py

import RPi.GPIO as GPIO
import time
import os

def main(args):

	ip = args.server_ip
	tag = args.hashtag
	
	# Read API/Dev keys from separate file
	

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