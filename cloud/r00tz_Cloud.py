from flask import Flask,redirect,url_for, render_template_string, request,session,send_from_directory  # Importing the Flask modules
import sqlite3
import json
import time
import os
import uuid

app = Flask(__name__)

PRODUCTNAME  = "r00tz Cloud Interface v1.0"

@app.route("/")
def dohome():
	with open('cloud_html/index.html') as f:
	   tpl = f.read()
	f.close()
	return render_template_string(tpl)

@app.route('/<path:path>')
def templatehtml(path):
	if path.endswith("html"): #vuln
		with open('cloud_html/%s' % path) as f:
		   tpl = f.read()
		f.close()
		return render_template_string(tpl)
	else:
		return send_from_directory('cloud_html', path)

@app.route('/cloud/<path:path>')
def app_templatehtml(path):
	if path.endswith("html"): #vuln
		with open('templatehtml/%s' % path) as f:
		   tpl = f.read()
		f.close()
		return render_template_string(tpl)
	else:
		return send_from_directory('templatehtml', path)
			
@app.context_processor
def context_proc():
	fsty = open(os.path.join("templatehtml","menustyle.txt"))
	fscr = open(os.path.join("templatehtml","menuscript.txt"))
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

@app.route("/api/getHomes", methods=['POST'])
def dogethomes():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		c.execute("select homes.house_id, homes.username, count(status) from homes left join switch_status on homes.house_id=switch_status.house_id group by homes.house_id;")
		status = {"result":"success", "status":c.fetchall()}
		return json.dumps(status)


@app.route("/api/getLogs", methods=['POST'])
def dogetlogs():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		c.execute("select * from logs order by ts desc limit 30;")
		status = {"result":"success", "status":c.fetchall()}
		return json.dumps(status)


@app.route("/api/getSwitches", methods=['POST'])
def dogetswitches():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		if "switch_id" in content:
			c.execute("select switch_id, switch_name, type, status from switch_status where switch_id='%s'" % content["switch_id"]) #sql injection
		elif "house_id" in content:
			c.execute("select switch_id, switch_name, type, status from switch_status where house_id='%s'" % content["house_id"]) #sql injection
		else:
			c.execute("select switch_id, switch_name, type, status from switch_status;")
		status = {"result":"success", "status":c.fetchall()}
		return json.dumps(status)


@app.route("/api/getState", methods=['POST'])
def dogetstatus():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		try:
			if "switch_id" in content:
				c.execute("select switch_name, type, status from switch_status where house_id=? and switch_id=?;",(content["house_id"],content["switch_id"]))
				logevent(content["house_id"], "house_id %s has requested status on switch %s" % (content["house_id"], content["switch_id"]))
				status = {"result":"success", "status":c.fetchone()}
			else:
				c.execute("select switch_id, switch_name, type, status from switch_status where house_id=?",(content["house_id"],))
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


@app.route("/api/registerSwitch", methods=['POST'])
def doregisterswitch():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		try:
			if  content["type"] in ["switch","rgbswitch", "dmxswitch"]:
				c.execute("select homes.house_id, count(status) from homes left join switch_status on homes.house_id=switch_status.house_id where  homes.house_id=? group by homes.house_id;",(content["house_id"],))
				(house_id, count) = c.fetchone()
				switch_id = "-".join(house_id.split("-")[:-1] + ["%012d" % (count,)])
				c.execute("insert into switch_status (switch_id,switch_name,house_id,type,status) values (?,?,?,?,?)" , (switch_id,content["switch_name"], content["house_id"], content["type"], json.dumps({"basicstate":"OFF","channelred":0,"channelgreen":0,"channelblue":0})))
				conn.commit()
				status = {"result":"success", "switch_id":switch_id}
				logevent(content["house_id"], "house_id %s is now registered" % (switch_id))
			else:
				status["error"] = "request for unssported switch type"
				logevent(content["house_id"], "house_id %s is now registered" % (switch_id))
		except:
			conn.rollback()
			status["error"] = "this switch already exists for this home"
			logevent(None, "error from ip address XXXX making registerswitch api query")
	else:
		status["error"] = "no json data provided"
		logevent(None, "non-json data from ip address XXXX making registerswitch api query")
	return json.dumps(status)


@app.route("/api/update", methods=['GET'])
def doupdate():
	status = {"version":"1.01", "file":"r00tzLights_1.0_fw.img"}
	return json.dumps(status)

	
@app.route("/api/register", methods=['POST'])
def doregister():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		print(content)
		try:
			house_id = str(uuid.uuid4()) #fixme, make this a sequential uuid value
			c.execute("insert into homes (house_id,username, password, admin, first, last, address, city, state, phone) values (?,?,?,0,?,?,?,?,?,?)" , (house_id,content["username"], content["password"], content["first"], content["last"], content["address"],content["city"],content["state"],content["phone"]))
			conn.commit()
			status = {"result":"success", "house_id":house_id}
			logevent(house_id, "house_id %s is now registered" % (house_id))
		except:
			conn.rollback()
			status["error"] = "this house already exists"
			logevent(None, "error from ip address XXXX making register api query")
	else:
		status["error"] = "no json data provided"
		logevent(None, "non-json data from ip address XXXX making register api query")

	return json.dumps(status)
		 
		 
@app.route("/api/setState", methods=['POST'])
def dosetstatus():
	status = {"result":"fail"}
	if request.is_json:
		conn = getdbconn()
		c = conn.cursor()
		content = request.get_json()
		state = json.loads(content["state"])
		try:
			try:
				c.execute("select status from switch_status where house_id=? and switch_id=?;",(content["house_id"],content["switch_id"]))
				cc = json.loads(c.fetchone()[0])
			except:
				cc = {"channelred":255,"channelgreen":255,"channelblue":255}
				
			if "channelred" in state:
				red = state['channelred']
			else:
				red = cc["channelred"]
			if "channelgreen" in state:
				green = state['channelgreen']
			else:
				green = cc["channelgreen"]
			if "channelblue" in state:
				blue = state['channelblue']
			else:
				blue  = cc["channelblue"]
				
			state = {"basicstate":state["basicstate"],"channelred":red,"channelgreen":green,"channelblue":blue}
			c.execute("update switch_status set status=? where house_id=? and switch_id=?" , (json.dumps(state),  content["house_id"],content["switch_id"]))
			conn.commit()
			status["result"] = "success"
			status["state"] = state
			logevent(content["house_id"], "house_id %s has set status %s on switch %s" % (content["house_id"], state["basicstate"], content["switch_id"]))
		except:
			conn.rollback()
			status["error"] = "the resource could not be located"
			logevent(None, "error from ip address XXXX making setState api query")
	else:
		status["error"] = "no json data provided"
		logevent(None, "non-json data from ip address XXXX making setState api query")
			
	return json.dumps(status)
	
	
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
	status = {"result":"fail"}
	conn = getdbconn()
	if request.is_json:
		c = conn.cursor()
		content = request.get_json()
		username = content['username']
		password = content['password']
		
	elif request.method == 'GET':
		username = request.args.get('username')
		password = request.args.get('password')
	try:
		c.execute("select password,house_id,admin from homes where username='%s'; " % (username,)) #injection
		row = c.fetchone()
		if row is not None:
			if  password == row[0]:
				session['loggedin'] = True
				session['house_id'] = row[1]
				session["admin"] = row[2]
				if  row[2]:
					logevent(row[1], "admin %s logged in",username)
				else:
					logevent(row[1], "user %s logged in",username)
					
				status["admin"] = row[2]
				status["house_id"] = session['house_id']
				status["result"] = "success"

			else:
				status["error"] =  "user %s  failed to logged in" % username
				logevent(row[1],status["error"])
		else:
			status["error"] =  "user is not found .. probably"
			logevent(None,status["error"])
	except:
		status["error"] ="error during login attempt"
		logevent(None, status["error"])
		
	if request.method == 'GET':
		return redirect("/cloud/logview.html")
		
	return json.dumps(status)

	
def logevent(house_id, eventstring):
	conn = getdbconn()
	c = conn.cursor()
	c.execute("insert into logs (ts, house_id,logmsg) values (?,?,?);", (time.time(), house_id,eventstring))
	conn.commit()


def buildDB(conn):
	conn.execute("create table if not exists logs(event_id INTEGER PRIMARY KEY AUTOINCREMENT, ts  integer, house_id text, logmsg  text);")
	conn.execute("create table IF NOT EXISTS homes(house_id text,username text, password text, admin integer, first text,last text,address text,city text,state text,phone text,  UNIQUE(house_id), UNIQUE(username));")
	conn.execute("create table IF NOT EXISTS switch_status(switch_id text,house_id text, switch_name text, type text, status text,  UNIQUE(switch_id,house_id), FOREIGN KEY(house_id) REFERENCES homes(house_id));")
	conn.commit()
	conn.execute("insert or REPLACE  into homes(house_id,username,password,admin, first,last,address,city,state,phone) values (Null,'admin', 'XouBL*Vr$3', 1, 'internal', 'only', Null,Null,Null,Null)")
	conn.commit()

app.secret_key = "any random string" #;)
app.config['DEBUG'] = True
conn = getdbconn()
buildDB(conn)

if __name__ == "__main__":
	logevent(None, "server started")
	app.run(host= '0.0.0.0',port=5001)

    

