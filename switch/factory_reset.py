from pathlib import Path
import os
import json
from update_switch_status import *

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
