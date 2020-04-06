from pathlib import Path
import os 


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

file =  os.path.join("logs","switchlog.txt ")
if os.path.exists(file): 
	os.remove(file)
	Path(file).touch()	 
