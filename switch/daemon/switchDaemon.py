#import daemon
import sys
import os
os.chdir("/home/pi/switch")
sys.path.insert(0, "/home/pi/switch")
from r00tzgpio import *
from update_switch_status import *
from util import *
import time
from util import *
import os
import struct
import json
import socket
import select

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


gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
gapi.all_leds_state(False)

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


if BUTTON_PRESSED_STATE == 0:
	GPIO.add_event_detect(INPUT_BUTTON_0_PIN, GPIO.FALLING, callback = switchbtn_event, bouncetime = 500)
	GPIO.add_event_detect(INPUT_BUTTON_1_PIN, GPIO.FALLING, callback = resetpress, bouncetime = 500)
else:
	GPIO.add_event_detect(INPUT_BUTTON_0_PIN, GPIO.RISING, callback = switchbtn_event, bouncetime = 500)
	GPIO.add_event_detect(INPUT_BUTTON_1_PIN, GPIO.RISING, callback = resetpress, bouncetime = 500)

relaystate = 0

def toggle_relay():
	global relaystate
	gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
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


def main_program():
	global relaystate
	CHECK_SWITCH_INTERVAL = 20
	CHECK_SWITCH_LAST_TIME = 0
	CHECK_UPDATE_INTERVAL = (60 * 60) * 15
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
				if relaystate == 0:
					gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
					rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
					gapi.led_on("relay_led")
					gapi.relay_on()
					rapi.apiSetStatus(getFile("r00tzSwitchID"),"ON")
					relaystate = 1
			else:
				if relaystate == 1:
					gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
					rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
					gapi.led_off("relay_led")
					gapi.relay_off()
					rapi.apiSetStatus(getFile("r00tzSwitchID"),"OFF")
					relaystate = 0



			if existsFile("r00tzRegistered"):
				gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
				rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
				if (CHECK_SWITCH_LAST_TIME + CHECK_SWITCH_INTERVAL) < time.time():
					print("cloud")
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
				gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
				rapi = r00tsIOTAPI(house_id=getFile("r00tzRegistered"),apicallupdate=lambda:gapi.led_blink("cloudapi"))
				try:
					ret = rapi.apiCheckUpdate()
					#fixme do update
				except:
					pass
				print("update")
				CHECK_UPDATE_LAST_TIME = time.time()


print("checking for factory reset")
if GPIO.input(INPUT_BUTTON_1_PIN) == BUTTON_PRESSED_STATE:
	gapi = getBestGPIOHandler(getFile("r00tzSwitchType"))
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
		time.sleep(5)
		
		while(GPIO.input(INPUT_BUTTON_1_PIN) != BUTTON_PRESSED_STATE):
			print("reboot required")
			gapi.led_on("firmware")
			time.sleep(1)
			gapi.led_off("firmware")
			time.sleep(1)
		#reboot
		
#with daemon.DaemonContext():
main_program()
 
