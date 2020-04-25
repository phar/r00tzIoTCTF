import requests
import uuid
import argparse
import os
import os.path as path
from pathlib import Path
import json
from r00tzgpio import *
from util import *


USE_TLS = False

class r00tsIOTAPI():
	def __init__(self, host="192.168.1.13", port=5001, house_id=None, apicallupdate=lambda: None):
		self.host = host
		self.port = port
		self.apicallupdate = apicallupdate
		if USE_TLS:
			self.api_host_url = "https://%s:%d" % (self.host, self.port)
		else:
			self.api_host_url = "http://%s:%d" % (self.host, self.port)
		self.house_id = house_id

	def api_request(self, api, data):
		ep = "%s/api/%s" % (self.api_host_url ,api)
		print(data)
		try:
			r = requests.post(url = ep, json = data, verify=False)
			self.apicallupdate()
			return r.json()
		except requests.exceptions.ConnectionError:
			return {"result":"failure"}
	
	
	def apiLogin(self, username,password):
		ret  = self.api_request("login", {"username":username,"password":password})
		if "house_id" in ret:
			self.house_id = ret["house_id"]
		return ret
		
	def apiSetStatus(self, switch_id, status, red=255,green=255, blue=255):
		if status in ["ON","on","On",1,True]:
			state = {"basicstate":"ON","channelred":red,"channelgreen":green,"channelblue":blue}
		else:
			state = {"basicstate":"OFF","channelred":0,"channelgreen":0,"channelblue":0}
		return self.api_request("setState", {"house_id":self.house_id,"switch_id":switch_id,"state":json.dumps(state)})

	def apiGetStatus(self, switch_id):
		return self.api_request("getState", {"house_id":self.house_id,"switch_id":switch_id})

	def apiCheckUpdate(self):
		return self.api_request("update", {})

	def apiRegisterHouse(self,username, password, first, last, address, city, state, phone):
		return self.api_request("register", {"username":username,"password":password, "first":first,"last":last,"address":address,"city":city,"state":state,"phone":phone})

	def apiRegisterSwitch(self,type, switch_name):
		return self.api_request("registerSwitch", {"house_id":self.house_id, "type":type, "switch_name":switch_name})

 
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
	parser.add_argument('--update', action="store_true", )
	parser.add_argument('--home_id', action="store", )
	parser.add_argument('--type', action="store", )

	results = parser.parse_known_args()[0]

	gapi = getBestGPIOHandler(results.type)
#	rapi = r00tsIOTAPI()


	if results.home_id:
		rapi = r00tsIOTAPI(house_id=results.home_id, apicallupdate=lambda:gapi.led_blink("cloudapi"))
#		r = rapi.apiLogin(home_id=results.home_id);
	else:
		rapi = r00tsIOTAPI(apicallupdate=lambda:gapi.led_blink("cloudapi"))
		r = rapi.apiLogin(results.username,results.password);
#	print(r)

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
		print(ret)
		if sgresults.updatestatus:
#			print(ret["status"][0])
			if ret["status"][1] == "ON":
				gapi.led_on("relay_led")
				gapi.relay_on()
			else:
				gapi.led_off("relay_led")
				gapi.relay_off()
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
			pass
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

