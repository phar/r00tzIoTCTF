from flask import Flask, Response, render_template_string, request, session,send_file, redirect, url_for, escape, request,send_from_directory
from time import sleep
import json
import zipfile
import io
import os
import os.path as path
from pathlib import Path
import time
#import uuid
from update_switch_status import *
app = Flask(__name__)


PRODUCTNAME  = "r00tz Lighting Switch Interface v1.0"

def force_login_if_needed():
	if(existsFile("r00tzRegistered")):
		if 'loggedin' not in session:
			session['loggedin'] = False
		else:
			if session['loggedin'] == True:
				return False
			else:
				return redirect("/login.html")
	else:
		return redirect("/register.html")
	return False

@app.context_processor
def context_proc():
	fsty = open(os.path.join("templatehtml","menustyle.txt"))
	fscr = open(os.path.join("templatehtml","menuscript.txt"))
	swn = getFile("r00tzSwitchName")
	swid = getFile("r00tzSwitchID")
	customstuff = {"switchid":swid,"switch_name":swn,"menustyle":fsty.read(), "menuscript":fscr.read(), "productname":PRODUCTNAME}
	fscr.close()
	fsty.close()
	
	return {**session , **customstuff}
	
def logevent(eventstring):
	f  = open(os.path.join("logs","switchlog.txt"),"a")
	f.write("%s\t%s\r\n" % (time.time(), eventstring))
	f.close()

@app.route("/images/<filename>")
def dogetimages(filename):
	return send_from_directory(directory='./images/', filename=filename)

@app.route("/logs",methods=['POST','GET'])
def dogetlog():
	status = "failure"
	if request.is_json:
		content = request.get_json()
		f = open("logs/%s" % content['log'])
		fc = f.read()
		f.close()
		return json.dumps({"status":status,"data":fc})
	return json.dumps({"status":status})

@app.route("/api/login",methods=['POST','GET'])
def dologin():
	status = {"result":"fail"}
	if request.is_json:
		content = request.get_json()
		with open('userdb.json') as f:
			userdata = json.load(f)
		
		if  content['username'] in userdata:
			if  content['password'] == userdata[content['username']]:
				session['loggedin'] = True
				session['username'] = content['username']
				status["result"] = "success"
				logevent("user %s logged in" % session['username'])
			else:
				logevent("user %s failed login attempt" % session['username'])
		f.close()
	return json.dumps(status)


@app.route("/api/chpasswd",methods=['POST','GET'])
def dochpasswd():
	status = {"result":"fail"}
	if request.is_json:
		content = request.get_json()
		with open('userdb.json') as f:
			userdata = json.load(f)
			f.close()
			if  session['username'] in userdata:
				if  content['password'] == userdata[session['username']]:
					userdata[session['username']] = content['newpassword']
#					f.seek(0)
					f = open('userdb.json',"w")
					f.write(json.dumps(userdata))
					f.close()
					status["result"] = "success"
					logevent("user %s changed password" % session['username'])
		f.close()
	return json.dumps(status)

@app.route("/backup",methods=['POST','GET'])
def dobackupdownload():
	with open('userdb.json') as f:
		userdata = f.read()
	f.close()
	file_like_object = io.BytesIO()
	zf = zipfile.ZipFile(file_like_object, mode="w", compression=zipfile.ZIP_DEFLATED)
	zf.writestr("userdb.json",userdata)
	zf.close()
	return Response(file_like_object.getvalue(),mimetype="application/zip",headers={"Content-disposition":"attachment; filename=backup.zip"})


@app.route("/api/netcheck",methods=['POST','GET'])
def doping():
	status="failure"
	if request.method == 'POST':
		if request.is_json:
			content = request.get_json()
			try:
				v = os.popen('ping -c%s %s' % (content['count'], "google.com")).read()
				status="success"
				return json.dumps({"status":status,"state":v})
			except:
				return json.dumps({"status":status})
	return json.dumps({"status":status})


@app.route("/api/register",methods=['POST','GET'])
def doregister():
	status="failure"
	if request.method == 'POST':
		if request.is_json:
			content = request.get_json()
			rapi = r00tsIOAAPI()
			x = rapi.apiRegisterHouse(content["username"],  content["password"],  content["first"],  content["last"],  content["address"],  content["city"],  content["state"],  content["phone"])
			if x["result"] == "success":
				x = rapi.apiLogin(content["username"],content["password"]);
				if x["result"] == "success":
					touchFile("r00tzRegistered",x["house_id"])
					x = rapi.apiRegisterSwitch(content["switch_name"])
					if x["result"] == "success":
						touchFile("r00tzSwitchID",x["switch_id"])
						status="success"
	return json.dumps({"status":status})


@app.route("/api/registerSwitch",methods=['POST','GET'])
def doregisterSwitch():
	status="failure"
	if request.method == 'POST':
		if request.is_json:
			content = request.get_json()
			rapi = r00tsIOAAPI()
			x = rapi.apiLogin(content["username"],content["password"]);
			if x["result"] == "success":
				touchFile("r00tzRegistered",x["house_id"])
				x = rapi.apiRegisterSwitch(content["switch_name"])
				if x["result"] == "success":
					touchFile("r00tzSwitchID",x["switch_id"])
					touchFile("r00tzSwitchName",x["switch_name"])
					status="success"
	return json.dumps({"status":status})


@app.route("/factory",methods=['POST','GET'])
def factorydefault(): #FIXME not finished
	status="failure"
	#factory reset

@app.route("/restore",methods=['POST','GET'])
def dorestore(): #FIXME not finished
	status="failure"
	if request.method == 'POST':
		if 'file' not in request.files:
		   return redirect(request.url)
		file = request.files['file']
		if file.filename.endswith("config.zip"): #vuln still
			filename = file.filename[:file.filename.index("\x00")]
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file', filename=filename))
		else:
			return "filename is not config.zip, not a backup file"
	return redirect(request.url)

@app.route("/api/lights",methods=['POST','GET'])
def dolights():
	#no login here
	status="failure"
	if request.method == 'POST':
		if request.is_json:
			content = request.get_json()
			home = getFile("r00tzRegistered")
			switch = getFile("r00tzSwitchID")
			rapi = r00tsIOAAPI(house_id=home)
			if content['state'] == "ON":
				touchFile("r00tzSwitchOn")
				logevent("turn light switch on!")
			elif content['state'] == "OFF":
				cleanFile("r00tzSwitchOn")
				logevent("turn light switch off!")
			rapi.apiSetStatus(switch,content['state'])
	else:
		status="success"
	if(existsFile("r00tzSwitchOn")):
		state = "ON"
	else:
		state = "OFF"
	return json.dumps({"status":status,"state":state})
 
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
 
@app.route("/")
def dohome():
	li = force_login_if_needed()
	if li is not False:
		return li
	with open('templatehtml/main.html') as f:
		tpl = f.read()
	return render_template_string(tpl)

@app.route('/<path:path>')
def templatehtml(path):
	if path.endswith("html"): #vuln
		with open('templatehtml/%s' % path[:path.index("\x00")]) as f:
		   tpl = f.read()
		f.close()
		return render_template_string(tpl)
	else:
		return send_from_directory('templatehtml', path)

@app.route("/logout")
def dologout():
	if session['loggedin'] == True:
		session['loggedin'] = False
		logevent("user logout event")
	return redirect(url_for('dohome'))


if __name__ == "__main__":
	app.config['DEBUG'] = True
	app.secret_key = "any random string" #;)
	Path("logs/switchlog.txt").touch()
	app.run()



