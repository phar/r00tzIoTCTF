from flask import Flask,redirect,url_for, render_template_string, request,session,send_from_directory  # Importing the Flask modules
import sqlite3
import json
import uuid
import time


app = Flask(__name__)

 
# which URL should call the associated function.
#@app.route("/")
#def home():
#    return render_template_string("BARL BARK")
#

	
#

PRODUCTNAME  = "r00tz Cloud Interface v1.0"

@app.route("/")
def dohome():
	with open('cloud_html/index.html') as f:
	   tpl = f.read()
	return render_template_string(tpl)

@app.route('/<path:path>')
def send_js(path):
	if path.endswith("html"): #vuln
		with open('cloud_html/%s' % path) as f:
		   tpl = f.read()
		return render_template_string(tpl)
	else:
		return send_from_directory('cloud_html', path)
 
@app.context_processor
def context_proc():
	fsty = open("templatehtml/menustyle.txt")
	fscr = open("templatehtml/menuscript.txt")
	customstuff = {"menustyle":fsty.read(), "menuscript":fscr.read(), "productname":PRODUCTNAME}
	fscr.close()
	fsty.close()
	return {**session , **customstuff}
 
def force_login_if_needed():
	if 'loggedin' not in session:
		session['loggedin'] = False
	else:
		if session['loggedin'] == True:
			return False
		else:
			return redirect(url_for('dologinhtml'))
	return False

def getdbconn():
	conn = sqlite3.connect('cloud_data.db')
	conn.execute("PRAGMA foreign_keys = ON;");
	return conn

@app.route("/api/getStatus", methods=['POST'])
def dogetstatus():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		try:
			if "switch_id" in content:
				c.execute("select status from switch_status where house_id=? and switch_id=?",(content["house_id"],content["switch_id"]))
				status = {"result":"success", "status":c.fetchone()[0]}
				logevent(content["house_id"], "house_id %s has requested status on switch %s" % (content["house_id"], content["switch_id"]))
			else:
				c.execute("select switch_id,status from switch_status where house_id=?",(content["house_id"],))				
				status = {"result":"success", "status":c.fetchall()}
				logevent(content["house_id"], "house_id %s has requested status" % (content["house_id"]))
		except:
			status["error"] = "the resource could not be located"
			logevent(None, "error from ip address XXXX making getStatus api query")
	else:
		status["error"] = "no json data provided"
		logevent(None, "non-json data from ip address XXXX making register api query")
	
	return json.dumps(status)
	
@app.route("/images/<filename>")
def dogetimages(filename):
	return send_from_directory(directory='./images/', filename=filename)


@app.route("/api/register", methods=['POST'])
def doregister():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		try:
			c.execute("insert into homes (house_id,username, password, first, last, address, city, state, phone) values (?,?,?,?,?,?,?,?,?)" , (content["house_id"],content["username"], content["password"], content["first"], content["last"], content["address"],content["city"],content["state"],content["phone"]))
			conn.commit()
			status = {"result":"success"}
			logevent(content["house_id"], "house_id %s is now registered" % (content["house_id"]))
		except:
			conn.rollback()
			status["error"] = "this house already exists"
			logevent(None, "error from ip address XXXX making register api query")
	else:
		status["error"] = "no json data provided"
		logevent(None, "non-json data from ip address XXXX making getStatus api query")

	print(status)
	return json.dumps(status)
		 
		 
@app.route("/api/setStatus", methods=['POST'])
def dosetstatus():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		#i should make this a sql ijection
		try:
			print(content)
			c.execute("insert or replace into switch_status (switch_id,house_id,status) values (?,?,?)" , (content["switch_id"], content["house_id"], content["status"]))
			status = {"result":"success", "status":content["status"]}
			conn.commit()
			logevent(content["house_id"], "house_id %s has set status %s on switch %s" % (content["house_id"], content["status"], content["switch_id"]))
		except:
			conn.rollback()
			status["error"] = "the resource could not be located"
			logevent(None, "error from ip address XXXX making setStatus api query")
	else:
		status["error"] = "no json data provided"
		logevent(None, "non-json data from ip address XXXX making setStatus api query")
			
	return json.dumps(status)
	

@app.route("/login")
def dologinhtml():
	with open('templatehtml/login.html') as f:
	   tpl = f.read()
	return render_template_string(tpl)
	
@app.route("/admin")
def doadminloginhtml():
	with open('templatehtml/admin.html') as f:
	   tpl = f.read()
	return render_template_string(tpl)
	
@app.route("/main")
def domain():
	with open('templatehtml/main.html') as f:
	   tpl = f.read()
	return render_template_string(tpl)
	
	
@app.route("/logout")
def dologout():
	if session['loggedin'] == True:
		session.clear()
		logevent(None,"user logout event")
	return redirect(url_for('dohome'))


@app.route("/api/login",methods=['POST','GET'])
def dologin():
	conn = getdbconn()
	c = conn.cursor()
	try:
		print(request.form['user'])
		c.execute("select password,house_id from homes where username=(?);", (request.form['user'],))
		row = c.fetchone()
		if  request.form['pass'] == row[0]:
			session['loggedin'] = True
			session['house_id'] = row[1]
			logevent(row[1], "user %s logged in")
		else:
			logevent(row[1], "user %s  failed to logged in" % request.form['user'])
	except:
		logevent(None, "database error during login attempt")
	return redirect(url_for('domain'))

	
def logevent(house_id, eventstring):
	conn = getdbconn()
	c = conn.cursor()
	c.execute("insert into logs (ts, house_id,logmsg) values (?,?,?);", (time.time(), house_id,eventstring))
	conn.commit()


def buildDB(conn):
	conn.execute("create table if not exists logs(event_id INTEGER PRIMARY KEY AUTOINCREMENT, ts  integer, house_id text, logmsg  text);")
	conn.execute("create table IF NOT EXISTS homes(house_id text,username text, password text, first text,last text,address text,city text,state text,phone text,  UNIQUE(house_id));")
	conn.execute("create table IF NOT EXISTS switch_status(switch_id text,house_id text, status integer, UNIQUE(switch_id,house_id), FOREIGN KEY(house_id) REFERENCES homes(house_id));")
	conn.commit()
	conn.execute("insert into homes(house_id,username,password,first,last,address,city,state,phone) values (Null,'admin', 'password', 'internal', 'only', Null,Null,Null,Null)")
	conn.commit()


if __name__ == "__main__":
	# Flask constructor takes the name of current module (__name__) as argument.
	# Enable debug mode
	app.secret_key = "any random string" #;)
	app.config['DEBUG'] = True
	conn = getdbconn()
	buildDB(conn)
	logevent(None, "server started")
	app.run(port=5001)

    
