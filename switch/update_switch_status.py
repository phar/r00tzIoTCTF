import requests
API_HOST_URL = "http://localhost:5000"


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


def apiRegisterHouse(house_id, password, first, last, address, city, state, phone):
	return api_request("register", {"house_id":house_id,"password":password,"first":first,"last":last,"address":address,"city":city,"state":state,"phone":phone})

 
# Run the app on the local development server
if __name__ == "__main__":
	home_id = "SdfsdfsD"
	print(apiRegisterHouse(home_id, "password","firsty","lasty","mocking bird lane","seattle","wa","23423423"))
	print(apiSetStatus(home_id,"bathroom lights",1))
	print(apiGetStatus(home_id,"bathroom lights"))
	print(apiSetStatus(home_id,"bathroom lights",0))
	print(apiGetStatus(home_id,"bathroom lights"))
	print(apiSetStatus(home_id,"bathroom lights",128))
	print(apiGetStatus(home_id,"bathroom lights"))
	print(apiSetStatus(home_id,"bathroom lights",0))
	print(apiGetStatus(home_id,"bathroom lights"))

