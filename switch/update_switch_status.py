import requests
import uuid
import argparse
import os
import os.path as path
from pathlib import Path
import json
from r00tzgpio import *

def touchFile(file, contents=None):
	f = open(os.path.join("configs", file),"w")
	ret =  json.dump(contents,f)
	f.close()
	return ret;
	
	
def getFile(file):
	if os.path.isfile(os.path.join("configs", file)):
		f = open(os.path.join("configs", file))
		ret =  json.load(f)
		f.close()
	else:
		return ""
	return ret
	

def cleanFile(file):
	if existsFile(file):
		os.remove(os.path.join("configs", file))
		
		
def existsFile(file):
	return path.isfile(os.path.join("configs", file))


def cleanLog(file):
	if existsFile(file):
		os.remove(os.path.join("logs", file))

def touchLog(file):
	f = open(os.path.join("logs", file),"w")
	f.close()


class r00tsIOAAPI():
	def __init__(self, host="localhost", port=5001, house_id=None, apicallupdate=lambda: None):
		self.host = host
		self.port = port
		self.api_host_url = "http://%s:%d" % (self.host, self.port)
		self.house_id = house_id

	def api_request(self, api, data):
		ep = "%s/api/%s" % (self.api_host_url ,api)
		r = requests.post(url = ep, json = data)
		apicallupdate()
		return r.json()

	def apiLogin(self, username,password):
		ret  = self.api_request("login", {"username":username,"password":password})
		self.house_id = ret["house_id"]
		return ret
		
	def apiSetStatus(self, switch_id, status):
		return self.api_request("setStatus", {"house_id":self.house_id,"switch_id":switch_id,"status":status})

	def apiGetStatus(self, switch_id):
		return self.api_request("getStatus", {"house_id":self.house_id,"switch_id":switch_id})

	def apiCheckUpdate(self):
		return self.api_request("update", {})

	def apiRegisterHouse(self, username, password, first, last, address, city, state, phone):
		return self.api_request("register", {"username":username,"password":password,"first":first,"last":last,"address":address,"city":city,"state":state,"phone":phone})

	def apiRegisterSwitch(self, switch_name):
		return self.api_request("registerSwitch", {"house_id":self.house_id, "switch_name":switch_name})

 
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='r00ts IoT API  Tool and Lib')

	parser.add_argument('--username', action="store", )
	parser.add_argument('--password', action="store", )
	parser.add_argument('--switch_name', action="store" )
	parser.add_argument('--set', action="store_true", )
	parser.add_argument('--get', action="store_true", )
	parser.add_argument('--register_house', action="store_true", )
	parser.add_argument('--register_switch', action="store_true", )
	parser.add_argument('--buttons', action="store_true", )

	results = parser.parse_known_args()[0]

	gapi = r00tsIoTGPIO()
	rapi = r00tsIOAAPI(apicallupdate=lambda:gapi.led_blink("cloudapi"))
	
	rapi.apiLogin(results.username,results.password);
	if results.set:
		parser.add_argument('--switch_id', action="store")
		parser.add_argument('--state', action="store", type=int)
		sgresults = parser.parse_args()
		print(sgresults)
		if sgresults.state > 0:
			state = "ON"
		else:
			state = "OFF"
		print(rapi.apiSetStatus(sgresults.switch_id,state))
	
	elif results.get:
		parser.add_argument('--switch_id', action="store")
		parser.add_argument('--updatestatus', action="store_true")
		sgresults = parser.parse_args()
		
		ret = rapi.apiGetStatus(sgresults.switch_id)
		if sgresults.update:
			if ret["state"] == "ON":
				rapi.led_on("relay_led")
				rapi.relay_on()
			else:
				rapi.led_off("relay_led")
				rapi.relay_off()
		print(ret)

	elif results.register_switch:
		sgresults = parser.parse_args()
		print(rapi.apiRegisterSwitch(sgresults.switch_name))
	
	elif results.register_house:
		parser.add_argument('--first', action="store", )
		parser.add_argument('--last', action="store", )
		parser.add_argument('--address', action="store", )
		parser.add_argument('--city', action="store", )
		parser.add_argument('--state', action="store", )
		parser.add_argument('--phone', action="store", )
		sgresults = parser.parse_args()
		print(rapi.apiRegisterHouse(sgresults.switch_id,sgresults.password,sgresults.first,sgresults.last,sgresults.address,sgresults.city,sgresults.state,sgresults.phone))

	elif results.update:
		parser.add_argument('--apply', action="store_true")
		sgresults = parser.parse_args()
		ret = rapi.apiCheckUpdate()
		if sgresults.apply:
			#fixme download the image
			#fixme unzip the image
			#fixme exectue update.sh

	elif results.buttons:
		parser.add_argument('--apply', action="store_true")
		sgresults = parser.parse_args()
		ret = gapi.get_buttonsDict()
		if sgresults.apply:
			if ret['factory_reset'] == True:
				print("factory reset")
			if ret['button1'] == True:
				print("i dont know what this button does yet")
		else:
			if ret['factory_reset'] == True:
				print("factory reset, but not actually applied")
			if ret['button1'] == True:
				print("i still dont know what this button does yet")

# python update_switch_status.py --home_id "Sdf34sdfsD"  --switch_id "bathroom lights" --register --username "foobar"  --password "password" --first "firsty" --last "lasty" --address "address" --city "city" --state="WA" --phone "92873492"
#update_switch_status.py  --username "foobar"  --password "password"  --switch_id "bathroom lights" --get
#update_switch_status.py --username "foobar"  --password "password"   --switch_id "bathroom lights" --set --state 0
#update_switch_status.py  --username "foobar"  --password "password"  --switch_id "bathroom lights" --set --state 1
#update_switch_status.py  --username "foobar"  --password "password"  --switch_id "bathroom lights" --registerSwitch
