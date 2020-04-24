import daemon
import sys
import os
os.chdir("/home/pi/switch")
sys.path.insert(0, "/home/pi/switch")
from r00tzgpio import *
from update_switch_status import *
from util import *
import time
from util import *

def resetbtn_event():
	pass
	
def switchbtn_event():
	if existsfileFile("r00tzSwitchOn"):
		clearFile("r00tzSwitchOn")
	else:
		touchFile("r00tzSwitchOn")

def main_program():
	CHECK_SWITCH_INTERVAL = 20
	CHECK_SWITCH_LAST_TIME = 0
	CHECK_UPDATE_INTERVAL = (60 * 60) * 15
	CHECK_UPDATE_LAST_TIME = 0
	
	relaystate = 0

	gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
	while True:
		if existsFile("r00tzSwitchOn"):
			if relaystate == 0:
				gapi.relay_on()
				relaystate = 1
		else:
			if relaystate == 1:
				gapi.relay_off()
				relaystate = 0

		if existsFile("r00tzRegistered"):
			house_id = getFile("r00tzRegistered")
			rapi = r00tsIOTAPI(house_id=house_id)
			if (CHECK_SWITCH_LAST_TIME + CHECK_SWITCH_INTERVAL) < time.time():
				ret = rapi.apiGetStatus(getFile("r00tzSwitchID"))
				print(ret["status"][2])
				status = json.loads(ret['status'][2])
				if status["basicstate"] == "ON":
					gapi.led_on("relay_led")
					gapi.relay_on()
				else:
					gapi.led_off("relay_led")
					gapi.relay_off()
				CHECK_SWITCH_LAST_TIME = time.time()

		if (CHECK_UPDATE_LAST_TIME + CHECK_UPDATE_INTERVAL) < time.time():
			ret = rapi.apiCheckUpdate()
			fixme do update
			CHECK_UPDATE_LAST_TIME = time.time()

			
		time.sleep(.25)

#with daemon.DaemonContext():
main_program()
