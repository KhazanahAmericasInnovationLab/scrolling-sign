

from firebase import firebase
import serial
import time
import datetime
from firebase.firebase import FirebaseApplication, FirebaseAuthentication
from kraken import kraken
import tweepy
from tweepy import OAuthHandler
import json

time.sleep(15)

SIGN_LENGTH = 26
CRYPTO_CHECK_INTERVAL = 60#in seconds

repetitions = 5
lastCheck = None
diff = None
firstcryptocheck = 1

ser = None

cryptocode = {
	'ETHUSD':'XETHZUSD',
	'XBTUSD':'XXBTZUSD',
	'LTCUSD':'XLTCZUSD',
	'ETHXBT':'XETHXXBT'
}

cryptocache = {
	'ETHUSD':0,
	'XBTUSD':0,
	'LTCUSD':0,
	'ETHXBT':0
}

def writeString(s, repetitions):
	for i in range(0, SIGN_LENGTH):
		time.sleep(0.01)
		ser.write(' ')

	for j in range(0, repetitions):
		for i in range(0, len(s)):
			time.sleep(0.01)
			ser.write(s[i])

		for i in range(0, SIGN_LENGTH/4):
			time.sleep(0.01)
			ser.write(' ')

	time.sleep(0.01)
	ser.write('~')

def gainstring(k, pair):
	delta = None
	if(firstcryptocheck==1):
		return " "
	try:
		delta = float(k.getTickerInfo(pair)['result'][cryptocode[pair]]['a'][0]) - float(cryptocache[pair])
	except Exception as inst:
		print inst
		delta = 0
	if (round(delta, 2)>=0):
		if (round(delta, 2)==0):
			if (str(round(delta, 2))[0]=='-'):
				return " +" + str(round(delta, 2))[1:]+" "
			return " +" + str(round(delta, 2))+" "
		return "[+" + str(round(delta, 2))+"]"
	else:
		return "{-" + str(round(delta, 2))[1:]+"}"


def pricestring(k, pair):
	price = None
	try:
		price = float(k.getTickerInfo(pair)['result'][cryptocode[pair]]['a'][0])
	except Exception as inst:
		print inst
		price = cryptocache[pair]
	return str(pair)+': '+str(round(price, 3)) + gainstring(k, pair) + "      "

def updatecache(k, pair):
	cryptocache[pair] = k.getTickerInfo(pair)['result'][cryptocode[pair]]['a'][0]





if __name__ == "__main__":
	k = kraken()
	ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout = 2)
	time.sleep(5)
	SECRET = '6FmRtZWFEupG9O140dJmr86XUfBcWxawvRkYAzar'
	DSN = 'https://scrolling-sign.firebaseio.com'
	EMAIL = 'dalyco884@gmail.com'
	authentication = FirebaseAuthentication(SECRET,EMAIL, True, True)
	firebase = FirebaseApplication(DSN, authentication)
	data = firebase.get('/data', None)
	mode = data['mode']
	showtext = "booting up..."

	consumer_key = data['twitter']['consumerkey']
	consumer_secret = data['twitter']['consumersecret']
	access_token = data['twitter']['accesstoken']
	access_secret = data['twitter']['accesssecret']

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)

	last = None
	lastCheck = datetime.datetime.now()
	diff = CRYPTO_CHECK_INTERVAL+1
	while True:
		print("refreshing")
		data = firebase.get('/data', None)
		mode = data['mode']
		print(mode)
		last = showtext
		if mode is 0:
			#MODE 0 = static text
			showtext = data['text']
			print(showtext)
			repetitions = 3
		elif mode is 1:
			showtext = datetime.datetime.now().weekday()
			if showtext is 0:
				showtext = data['monday']
			elif showtext is 1:
				showtext = data['tuesday']
			elif showtext is 2:
				showtext = data['wednesday']
			elif showtext is 3:
				showtext = data['thursday']
			elif showtext is 4:
				showtext = data['friday']
			elif showtext is 5:
				showtext = data['saturday']
			elif showtext is 6:
				showtext = data['sunday']
			print(showtext)
			repetitions = 8
		elif mode is 2:
			if (diff>CRYPTO_CHECK_INTERVAL):
				pair = data['crypto']['pair']
				if (pair=='all'):
					showtext = pricestring(k, 'ETHUSD')
					showtext = showtext + pricestring(k, 'XBTUSD')
					showtext = showtext + pricestring(k, 'LTCUSD')
					showtext = showtext + pricestring(k, 'ETHXBT')
					repetitions = 5
				else:
					showtext = pricestring(k, pair)
					repetitions = 6
				updatecache(k, 'ETHUSD')
				updatecache(k, 'XBTUSD')
				updatecache(k, 'LTCUSD')
				updatecache(k, 'ETHXBT')
				firstcryptocheck = 0
				lastCheck = datetime.datetime.now()
				print showtext
		elif mode is 3:
			showtext = ""
			g = 0
			for tweet in tweepy.Cursor(api.user_timeline, id=data['twittersn'], count=3).items():
   				showtext = showtext + "@"+str(data['twittersn'].encode('utf-8'))+": "+tweet.text+"   "
				g = g + 1
				if (g>=3):
					break
				
			repetitions = 1
		diff = (datetime.datetime.now()-lastCheck).seconds
                print(diff)

		if (last!= showtext):
			writeString(showtext.encode('utf-8'), repetitions)
			last = showtext
			print ('it different')
