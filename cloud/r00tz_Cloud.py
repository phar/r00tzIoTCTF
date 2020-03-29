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
	return send_from_directory('cloud_html', "index.html")

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
			c.execute("select status from switch_status where house_id=? and switch_id=?",(content["house_id"],content["switch_id"]))
			status = {"result":"success", "status":c.fetchone()[0]}
			logevent(content["house_id"], "house_id %s has requested status on switch %s" % (content["house_id"], content["switch_id"]))
		except:
			status["error"] = "the resource could not be located"
			logevent(None, "error from ip address XXXX making getStatus api query")
	else:
		status["error"] = "no json data provided"
		logevent(None, "non-json data from ip address XXXX making register api query")
	
	return json.dumps(status)
	
	
@app.route("/api/register", methods=['POST'])
def doregister():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		try:
			c.execute("insert into homes (house_id, password, first, last, address, city, state, phone) values (?,?,?,?,?,?,?,?)" , (content["house_id"], content["password"], content["first"], content["last"], content["address"],content["city"],content["state"],content["phone"]))
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
			c.execute("insert or replace into switch_status (switch_id,house_id,status) values (?,?,?)" , (content["switch_id"], content["house_id"], content["status"]))
			status = {"result":"success", "status":content["status"]}
			conn.commit()
			logevent(content["house_id"], "house_id %s has set status %d on switch %s" % (content["house_id"], content["status"], content["switch_id"]))
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
	
@app.route("/api/login",methods=['POST','GET'])
def dologin():
#	with open('userdb.json') as f:
#		userdata = json.load(f)

	conn = getdbconn()
	c = conn.cursor()
	content = request.get_json()
	try:
		c.execute("select password from homes where house_id=?", content['house_id'])

		if  request.form['user'] in userdata:
			if  request.form['pass'] == c.fetchone()[0]:
				session['loggedin'] = True
	except:
		pass
	return redirect(url_for('dohome'))

	
def logevent(house_id, eventstring):
	conn = getdbconn()
	c = conn.cursor()
	c.execute("insert into logs (ts, house_id,logmsg) values (?,?,?);", (time.time(), house_id,eventstring))
	conn.commit()


def buildDB(conn):
	conn.execute("create table if not exists logs(event_id INTEGER PRIMARY KEY AUTOINCREMENT, ts  integer, house_id text, logmsg  text);")
	conn.execute("create table IF NOT EXISTS homes(house_id text, password text, first text,last text,address text,city text,state text,phone text,  UNIQUE(house_id));")
	conn.execute("create table IF NOT EXISTS switch_status(switch_id text,house_id text, status integer, UNIQUE(switch_id,house_id), FOREIGN KEY(house_id) REFERENCES homes(house_id));")
	conn.commit()
	conn.execute("insert into homes(house_id,password,first,last,address,city,state,phone) values (Null, Null, 'internal', 'only', Null,Null,Null,Null)")
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

    
