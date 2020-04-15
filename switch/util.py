import os
import os.path as path
from pathlib import Path
import json

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


