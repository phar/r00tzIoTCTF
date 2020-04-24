import daemon
from r00tzgpio import *
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

CHECK_SWITCH_INTERVAL = 60
CHECK_SWITCH_LAST_TIME = 0
CHECK_UPDATE_INTERVAL = (60 * 60) * 15
CHECK_UPDATE_LAST_TIME = 0

def main_program():
	gapi = getBestGPIOHandler(getFile("r00tzSwitchType"), switchpress=switchbtn_eventm resetpress=resetbtn_event, logfunc=logevent)
    while True:
		if existsFile(r00tzSwitchOn):
			gapi.relay_on()
		else:
			gapi.relay_off()
			
		if existsfileFile("r00tzRegistered"):
			if (CHECK_SWITCH_LAST_TIME + CHECK_UPDATE_INTERVAL) < time.time()
				ret = rapi.apiGetStatus(getFile("r00tzSwitchID"))
				if ret["status"][1] == "ON":
					gapi.led_on("relay_led")
					gapi.relay_on()
				else:
					gapi.led_off("relay_led")
					gapi.relay_off()
				CHECK_SWITCH_LAST_TIME = time.time()

		if (CHECK_UPDATE_LAST_TIME + CHECK_UPDATE_INTERVAL) < time.time()
			ret = rapi.apiCheckUpdate()
			#fixme do update
			CHECK_UPDATE_LAST_TIME = time.time()

			
		time.sleep(.25)

with daemon.DaemonContext():
    main_program()
 
