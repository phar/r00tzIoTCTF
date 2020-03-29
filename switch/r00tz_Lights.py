from flask import Flask, Response, render_template_string, request, session,send_file, redirect, url_for, escape, request,send_from_directory  # Importing the Flask modules
from time import sleep      # Import sleep module from time library to add delays
import json
import zipfile
import io
import os
import os.path as path
from pathlib import Path
import time


app = Flask(__name__)

def force_login_if_needed():
#	if(existsFile("r00tzRegistered")):
		if 'loggedin' not in session:
			session['loggedin'] = False
		else:
			if session['loggedin'] == True:
				return False
			else:
				return redirect(url_for('dologinhtml'))
#	else:
#		redirect(url_for('doregisterhtml'))
#	return False


PRODUCTNAME  = "r00tz Lighting Switch Interface v1.0"


@app.context_processor
def context_proc():
	fsty = open("templatehtml/menustyle.txt")
	fscr = open("templatehtml/menuscript.txt")
	customstuff = {"menustyle":fsty.read(), "menuscript":fscr.read(), "productname":PRODUCTNAME}
	fscr.close()
	fsty.close()
	return {**session , **customstuff}
	
def logevent(eventstring):
	f  = open("logs/switchlog.txt","a")
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
	#except:
	return json.dumps({"status":status})

@app.route("/api/login",methods=['POST','GET'])
def dologin():
	with open('userdb.json') as f:
		userdata = json.load(f)
	if  request.form['user'] in userdata:
		if  request.form['pass'] == userdata[request.form['user']]:
			session['loggedin'] = True
			logevent("user %s logged in" % request.form['user'])
		else:
			logevent("user %s failed login attempt" % request.form['user'])

	return redirect(url_for('dohome'))

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


@app.route("/api/lights",methods=['POST','GET'])
def dolights():
	#no login here
	status="failure"
	if request.method == 'POST':
		if request.is_json:
			content = request.get_json()
			if content['state'] == "ON":
				touchFile("r00tzSwitchOn")
				logevent("turn light switch on!")
			elif content['state'] == "OFF":
				cleanFile("r00tzSwitchOn")
				logevent("turn light switch off!")
	else:
		status="success"
	if(existsFile("r00tzSwitchOn")):
		state = "ON"
	else:
		state = "OFF"
	return json.dumps({"status":status,"state":state})
 
def touchFile(file):
	Path(os.path.join("/tmp", file)).touch()
	
def cleanFile(file):
	if existsFile(file):
		os.remove(os.path.join("/tmp", file))

def existsFile(file):
	return path.isfile(os.path.join("/tmp", file))
 
# which URL should call the associated function.
@app.route("/")
def dohome():
	li = force_login_if_needed()
	if li is not False:
		return li

	with open('templatehtml/main.html') as f:
		tpl = f.read()
	return render_template_string(tpl)
	
@app.route("/register")
def doregister():
	if(existsFile("r00tzRegistered")):
		return redirect(url_for('dologinhtml'))
	else:
		with open('templatehtml/register.html') as f:
			tpl = f.read()
		return render_template_string(tpl)
	
@app.route("/login")
def dologinhtml():
	with open('templatehtml/login.html') as f:
	   tpl = f.read()
	return render_template_string(tpl)

@app.route("/viewlog")
def dologhtml():
	li = force_login_if_needed()
	if li is not False:
		return li
	with open('templatehtml/logview.html') as f:
	   tpl = f.read()
	return render_template_string(tpl)
	
@app.route("/netcheck")
def donetcheckhtml():
	li = force_login_if_needed()
	if li is not False:
		return li
	with open('templatehtml/netcheck.html') as f:
	   tpl = f.read()
	return render_template_string(tpl)

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

    
#TODO: store light switch state
#TODO: store initalization state
#TODO: new  switch registration
#TODO: restore factory defaults
#TODO: more logging
