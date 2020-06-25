#import daemon
import sys
import os
HOMEPATH = "/home/pi/flaskapp" #this line is rewritten by SED
HOMEDIR = "/home/pi/" #this line is rewritten by SED
os.chdir(HOMEPATH)
sys.path.insert(0, HOMEPATH)
from r00tzgpio import *
from r00tzCloudApi import *
from util import *
import time
from util import *
import os
import struct
import json
import socket
import select
#import dmx.dmx as dmx


server_address = '/tmp/r00tzGPIOShimSocket'

def resetbtn_event(arv):
	pass
	
def switchbtn_event(arg):
	if existsFile("r00tzSwitchOn"):
		cleanFile("r00tzSwitchOn")
		
	else:
		touchFile("r00tzSwitchOn")
	toggle_relay()

def handle_command(gapi, command, args):
	logs = []
	print("enter")
	logs.append("logmessage")
	input = None
	
	if command == "led_blink":
		gapi.led_blink(args[0],args[1])
	elif command == "led_on":
		gapi.led_on(args[0])
	elif command == "led_off":
		gapi.led_on(args[1])
	elif command == "relay_on":
		gapi.led_on("relay_led")
		gapi.relay_on()
	elif command == "relay_off":
		gapi.led_off("relay_led")
		gapi.relay_off()
	elif command == "get_buttons":
		input = gapi.get_buttons()
	elif command == "get_buttonsDict":
		input = gapi.get_buttonsDict()
	elif command == "all_leds_state":
		gapi.all_leds_state(args[0])
		
	print("leave")
	return (True,input, logs)


try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

os.umask(0)
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(server_address)
sock.listen(1)
poller  = select.poll()
poller.register(sock, select.POLLIN)

def resetpress(arg):

	print("resetpress")

BUTTONMAP = {"factory_reset":INPUT_BUTTON_0_PIN,
		"switch":INPUT_BUTTON_1_PIN}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for n,b in BUTTONMAP.items():
	GPIO.setup(b, GPIO.IN)
	
if BUTTON_PRESSED_STATE == 0:
	GPIO.add_event_detect(INPUT_BUTTON_0_PIN, GPIO.FALLING, callback = switchbtn_event, bouncetime = 500)
	GPIO.add_event_detect(INPUT_BUTTON_1_PIN, GPIO.FALLING, callback = resetpress, bouncetime = 500)
else:
	GPIO.add_event_detect(INPUT_BUTTON_0_PIN, GPIO.RISING, callback = switchbtn_event, bouncetime = 500)
	GPIO.add_event_detect(INPUT_BUTTON_1_PIN, GPIO.RISING, callback = resetpress, bouncetime = 500)

relaystate = 0
colorstate = getFile("r00tzSwitchColor")

def toggle_relay(gapi):
	global relaystate
	rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
	if existsFile("r00tzSwitchOn"):
		if relaystate == 0:
			gapi.led_on("relay_led")
			gapi.relay_on()
			rapi.apiSetStatus(getFile("r00tzSwitchID"),"ON")
			relaystate = 1
	else:
		if relaystate == 1:
			gapi.led_off("relay_led")
			gapi.relay_off()
			rapi.apiSetStatus(getFile("r00tzSwitchID"),"OFF")
			relaystate = 0

def main_program(gapi):
	global relaystate
	CHECK_SWITCH_INTERVAL = 20
	CHECK_SWITCH_LAST_TIME = 0
	CHECK_UPDATE_INTERVAL = (60 * 60) * 15 #fixme, put these in configs
	CHECK_UPDATE_LAST_TIME = 0

	while True:
		fdVsEvent = poller.poll(250)
		if len(fdVsEvent):
			connection, client_address = sock.accept()
			logs = []
			try:
				dl = connection.recv(struct.calcsize("I"))
				rdl = struct.unpack("I",dl)[0]
				d = json.loads(connection.recv(rdl))
				r,input,logs = handle_command(gapi, d["command"], d["args"])
				a = {"result":r,"logs":logs}
			except:
				a = {"result":"failure!","logs":logs}
			
			try:
				s = json.dumps(a).encode()
				l = struct.pack("I",len(s))
				connection.sendall(l+s)
			except:
				pass
			connection.close()
		else:


			if existsFile("r00tzSwitchOn"):
				if relaystate == 0 or (colorstate != getFile("r00tzSwitchColor")):
					rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
					gapi.led_on("relay_led")
					gapi.relay_on()
					rapi.apiSetStatus(getFile("r00tzSwitchID"),"ON")
					relaystate = 1
					colorstate = getFile("r00tzSwitchColor")
			else:
				if relaystate == 1:
					rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
					gapi.led_off("relay_led")
					gapi.relay_off()
					rapi.apiSetStatus(getFile("r00tzSwitchID"),"OFF")
					relaystate = 0

			if existsFile("r00tzRegistered"):
				if (CHECK_SWITCH_LAST_TIME + CHECK_SWITCH_INTERVAL) < time.time():
					rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
					ret = rapi.apiGetStatus(getFile("r00tzSwitchID"))
					if(ret["result"] == "success"):
						status = json.loads(ret['status'][2])
						if status["basicstate"] == "ON":
							touchFile("r00tzSwitchOn")
						else:
							cleanFile("r00tzSwitchOn")
							gapi.relay_off()
					CHECK_SWITCH_LAST_TIME = time.time()

			if (CHECK_UPDATE_LAST_TIME + CHECK_UPDATE_INTERVAL) < time.time():
				rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
				try:
					ret = rapi.apiCheckUpdate()
					#fixme do update
					
					#download the file
					if getFile("r00tzUseTLSFlag") == True:
						self.api_host_url = "https://%s:%d" % (self.host, self.port)
					else:
						self.api_host_url = "http://%s:%d" % (self.host, self.port)
					ep = "%s/r00tzLights.fwupdate" % (self.api_host_url)
					localfile = "/tmp/r00tzLights.fwupdate"
					r = requests.get(url = ep, verify=False)
					f = open(localfile,"wb")
					f.write(r.text)
					f.close()
					factoryfile = os.path.join(HOMEPATH,localfile)
					os.system("tar -C %s -cjvpf %s/configs_package.tbz configs" % (HOMEPATH,HOMEDIR)) #backup configs
					os.system("rm -rf %s" % HOMEPATH)
					os.system("tar -xjvpf %s --overwrite" % localfile)
					os.system("tar -C %s  -xjvpf %s/configs_package.tbz" % (HOMEPATH,HOMEDIR)) #restore configs
					os.system("sudo -u www-data /bin/bash %s/update.sh" % HOMEPATH)

				except:
					pass
				print("update")
				CHECK_UPDATE_LAST_TIME = time.time()


if __name__ == "__main__":
	gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
	gapi.all_leds_state(False)

	print("checking for factory reset")
	if GPIO.input(INPUT_BUTTON_1_PIN) == BUTTON_PRESSED_STATE:
		print("set is held")
		aborted = 0
		for i in range(10,0,-1):
			gapi.led_blink("firmware")
			if GPIO.input(INPUT_BUTTON_1_PIN) != BUTTON_PRESSED_STATE:
				print("reset aborted")
				aborted = 1
				break
			print(i)
			time.sleep(1)
		if aborted == 0:
			print("factory reset condition")
			gapi.led_on("firmware")

			factoryfile = os.path.join(HOMEDIR,"factory_reset.tbz")
			os.system("rm -rf %s" % HOMEPATH)
			os.system("tar -xjvpf %s -C %s --overwrite" % (factoryfile, HOMEPATH))

			while(GPIO.input(INPUT_BUTTON_1_PIN) != BUTTON_PRESSED_STATE):
				print("reboot required")
				gapi.led_on("firmware")
				time.sleep(1)
				gapi.led_off("firmware")
				time.sleep(1)
			#reboot
			os.system('reboot')
		
		
	#if len(sys.argv) != 1: #any argument will provide an interactive mode
	#	with daemon.DaemonContext():
	#		main_program()
	#else:

	main_program(gapi)
