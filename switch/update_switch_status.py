import requests
import uuid
import argparse


API_HOST_URL = "http://localhost:5001"


#import RPi.GPIO as GPIO # Importing the GPIO library to control GPIO pins of Raspberry Pi
#
## Pins where we have connected servos
#servo_pin = 26
#servo_pin1 = 19
#
#GPIO.setmode(GPIO.BCM)  # We are using the BCM pin numbering
## Declaring Servo Pins as output pins
#GPIO.setup(servo_pin, GPIO.OUT)
#GPIO.setup(servo_pin1, GPIO.OUT)
#
## Created PWM channels at 50Hz frequency
#p = GPIO.PWM(servo_pin, 50)
#p1 = GPIO.PWM(servo_pin1, 50)
#
## Initial duty cycle
#p.start(0)
#p1.start(0)
#
## Get slider Values
#slider1 = request.form["slider1"]
#slider2 = request.form["slider2"]
## Change duty cycle
#p.ChangeDutyCycle(float(slider1))
#p1.ChangeDutyCycle(float(slider2))
## Give servo some time to move
#sleep(1)
## Pause the servo
#p.ChangeDutyCycle(0)
#p1.ChangeDutyCycle(0)
#return render_template_string(TPL)
 
 

def api_request(api, data):
	ep = "%s/api/%s" % (API_HOST_URL,api)
	r = requests.post(url = ep, json = data)
	return r.json()

def apiSetStatus(house_id, switch_id, status):
	return api_request("setStatus", {"house_id":house_id,"switch_id":switch_id,"status":status})

def apiGetStatus(house_id, switch_id):
	return api_request("getStatus", {"house_id":house_id,"switch_id":switch_id})


def apiRegisterHouse(house_id,username, password, first, last, address, city, state, phone):
	return api_request("register", {"house_id":house_id,"username":username,"password":password,"first":first,"last":last,"address":address,"city":city,"state":state,"phone":phone})

 
# Run the app on the local development server
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='r00ts IoT API  Tool and Lib')

	parser.add_argument('--username', action="store", )
	parser.add_argument('--password', action="store", )
	parser.add_argument('--home_id', action="store")
	parser.add_argument('--switch_id', action="store" )
	parser.add_argument('--set', action="store_true", )
	parser.add_argument('--get', action="store_true", )
	parser.add_argument('--register', action="store_true", )

	results = parser.parse_known_args()[0]
	print(results)
	if results.set:
		parser.add_argument('--state', action="store", type=int)
		sgresults = parser.parse_args()
		print(sgresults)
		if sgresults.state > 0:
			state = "ON"
		else:
			state = "OFF"
		print(apiSetStatus(sgresults.home_id,sgresults.switch_id,state))
	
	elif results.get:
		parser = parser.parse_args()
		print(apiGetStatus(parser.home_id,parser.switch_id))

	elif results.register:
		parser.add_argument('--first', action="store", )
		parser.add_argument('--last', action="store", )
		parser.add_argument('--address', action="store", )
		parser.add_argument('--city', action="store", )
		parser.add_argument('--state', action="store", )
		parser.add_argument('--phone', action="store", )
		sgresults = parser.parse_args()
		print(apiRegisterHouse(sgresults.home_id,sgresults.switch_id,sgresults.password,sgresults.first,sgresults.last,sgresults.address,sgresults.city,sgresults.state,sgresults.phone))
	
# python update_switch_status.py --home_id "Sdf34sdfsD"  --switch_id "bathroom lights" --register --username "foobar"  --password "password" --first "firsty" --last "lasty" --address "address" --city "city" --state="WA" --phone "92873492"
#update_switch_status.py  --username "foobar"  --password "password" --home_id "SdfsdfsD"  --switch_id "bathroom lights" --get
#update_switch_status.py --username "foobar"  --password "password"  --home_id "SdfsdfsD"  --switch_id "bathroom lights" --set --state 0
#update_switch_status.py  --username "foobar"  --password "password" --home_id "SdfsdfsD"  --switch_id "bathroom lights" --set --state 1
