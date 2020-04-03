from flask import Flask, Response, render_template_string, request, session,send_file, redirect, url_for, escape, request,send_from_directory
from time import sleep
import json
import zipfile
import io
import os
import os.path as path
from pathlib import Path
import time
import uuid
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
		return redirect("/login.html")
	return False

@app.context_processor
def context_proc():
	fsty = open(os.path.join("templatehtml","menustyle.txt"))
	fscr = open(os.path.join("templatehtml","menuscript.txt"))
	swid = getFile("r00tzSwitchID")
	customstuff = {"switchid":swid,"menustyle":fsty.read(), "menuscript":fscr.read(), "productname":PRODUCTNAME}
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
	
		print(content['log'])
		f = open("logs/%s" % content['log'])
		fc = f.read()
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
				status["result"] = "success"
				logevent("user %s logged in" % content['username'])
			else:
				logevent("user %s failed login attempt" % content['username'])
	return json.dumps(status)


@app.route("/backup",methods=['POST','GET'])
def dobackupdownload():
	with open('userdb.json') as f:
		userdata = f.read()
	file_like_object = io.BytesIO()
	zf = zipfile.ZipFile(file_like_object, mode="w", compression=zipfile.ZIP_DEFLATED)
	zf.writestr("userdb.json",userdata)
	zf.close()
	print (file_like_object.getvalue())
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
				x = rapi.apiRegisterSwitch(content["switch_id"])
				if x["result"] == "success":
					touchFile("r00tzRegistered")
			return x
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
				x = rapi.apiRegisterSwitch(content["switch_id"])
				if x["result"] == "success":
					touchFile("r00tzRegistered")
					status="success"
			return x
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
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
			
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file', filename=filename))
	return redirect(request.url)


@app.route("/api/lights",methods=['POST','GET'])
def dolights():
	#no login here
	status="failure"
	if request.method == 'POST':
		if request.is_json:
			content = request.get_json()
			home = getFile("r00tzSwitchID")
			rapi = r00tsIOAAPI(house_id=home)
			print(content)
			if content['state'] == "ON":
				touchFile("r00tzSwitchOn")
				logevent("turn light switch on!")
			elif content['state'] == "OFF":
				cleanFile("r00tzSwitchOn")
				logevent("turn light switch off!")
			rapi.apiSetStatus(home,content['state'])
	else:
		status="success"
	if(existsFile("r00tzSwitchOn")):
		state = "ON"
	else:
		state = "OFF"
	return json.dumps({"status":status,"state":state})
 
def touchFile(file, contents=None):
	f = open(os.path.join("configs", file),"w")
	return json.dump(contents,f)
	
def getFile(file):
	f = open(os.path.join("configs", file))
	return json.load(f)

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
		with open('templatehtml/%s' % path) as f:
		   tpl = f.read()
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
	if(not existsFile("r00tzSwitchID")):
		touchFile("r00tzSwitchID",str(uuid.uuid4()))
		logevent("created new switch uuid")

	app.run()



