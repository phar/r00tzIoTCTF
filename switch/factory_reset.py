from pathlib import Path
import os
import json


file =  os.path.join("configs","r00tzRegistered")
if os.path.exists(file): 
	os.remove(file) 

file =  os.path.join("configs","r00tzSwitchID")
if os.path.exists(file): 
	os.remove(file) 

file =  os.path.join("configs","r00tzSwitchOn")
if os.path.exists(file): 
	os.remove(file) 

file =  os.path.join("configs","r00tzSwitchName")
if os.path.exists(file): 
	os.remove(file) 

file =  os.path.join("logs","switchlog.txt")
if os.path.exists(file): 
	os.remove(file)
	Path(file).touch()	 


file =  os.path.join("logs","userdb.json")
userdb = {"admin": "admin", "backdoor": "r00tzrulez"}
if os.path.exists(file):
	os.remove(file)
f = open(file,"w")
json.dump(userdb,f)
f.close()
