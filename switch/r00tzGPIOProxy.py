import socket
import sys
import struct
import json
import time

server_address = '/tmp/r00tzGPIOShimSocket'

def lmbdaproxy(x):
	print(x)


class r00tsIoTGPIOProxy():
	def __init__(self,type, logfunc=lambda x: lmbdaproxy(x)):
		self.name = "proxy"
		self.logfunc =  logfunc
		self.type = type
		
	def logger(self, msg):
		self.logfunc("%s: %s" % (self.name,msg))

	def get_buttons(self):
			return self._send_command("get_buttons",[])

	def get_buttonsDict(self):
		return self._send_command("get_buttons",[]) #fixme

	def led_state(self,led,state):
		if state:
			return self.led_on(led)
		else:
			return  self.led_off(led)
			
	def all_leds_state(self,state):
		return self._send_command("all_leds_state",[state])
		
	def led_on(self,led):
		return self._send_command("led_on", [led])
		self.logger("led %s on" % led)

	def led_off(self,led):
		return self._send_command("led_off", [led])
		self.logger("led %s off" % led)

	def relay_on(self):
		return self._send_command("relay_on",[])
		self.logger("relay on")

	def relay_off(self):
		return self._send_command("relay_off",[])
		self.logger("relay off")
		
	def relay_state(self,state):
		if state:
			return self.relay_on()
		else:
			return self.relay_off()

	def led_blink(self,led, duration=.05):
		self._send_command("led_blink",[led,duration])
		self.logger("led %s blink with duration %f" % (led,duration))

	def _send_command(self, command,args = None):
		try:
			sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			sock.connect(server_address)
			res = False
			try:
				a = {"command":command,"args":args}
				s = json.dumps(a).encode()
				l = struct.pack("I",len(s))
				sock.sendall(l+s)
				srl = sock.recv(struct.calcsize("I"))
				rl = struct.unpack("I",srl)[0]
				resp = json.loads(sock.recv(rl))
				res = resp["result"]
				for l in resp["logs"]:
					self.logger(l)
			finally:
				sock.close()
			return res
		except:
			return False

if __name__ == "__main__":
	f = r00tsIoTGPIOProxy("switch", logfunc=lambda x: lmbdaproxy(x))
	while(1):
		f.led_blink("status0",)
		time.sleep(1)
		f.relay_on()
		time.sleep(1)
		f.relay_off()
