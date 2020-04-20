from r00tzgpio import *
import os
import json
from util import *


gapi = r00tsIoTGPIO()#logfunc=logevent) fixme actually log
btns = gapi.get_buttonsDict()
if btns["factory_reset"]: #factory reset is pressed
	time.sleep(5)
	btns = gapi.get_buttonsDict()
	if btns["factory_reset"]: #still pressed?
		file =  os.path.join("configs","r00tzRegistered")

		if os.path.exists(file):
			os.remove(file)

		cleanFile("r00tzRegistered")
		cleanFile("r00tzSwitchID")
		cleanFile("r00tzSwitchOn")
		cleanFile("r00tzSwitchName")

		cleanFile("r00tzUserDB")
		touchFile("r00tzUserDB",{"admin": "admin", "backdoor": "r00tzrulez"})

		cleanLog("switchlog.txt")
		touchLog("switchlog.txt")
