import random
import RPi.GPIO as GPIO
import time
#B+ or zero

STATUS_LED_0_PIN  = 6
STATUS_LED_1_PIN  = 13
STATUS_LED_2_PIN  = 19
STATUS_LED_3_PIN  = 26
IOT_SWITCH_PIN =  5
INPUT_BUTTON_0_PIN = 20
INPUT_BUTTON_1_PIN = 21
BUTTON_PRESSED_STATE =  0
BUTTON_RELEASED_STATE = 1


		
LEDMAP = {	"status0":STATUS_LED_0_PIN,
			"cloudapi":STATUS_LED_1_PIN,
			"firmware":STATUS_LED_2_PIN,
			"relay_led":STATUS_LED_3_PIN}

def lmbdaproxy(x):
	print(x)


class r00tsIoTGPIOBase():
	def __init__(self,  switchpress=lambda: None,resetpress=lambda: None,logfunc=lambda x: lmbdaproxy(x)):
		self.name = "base"
		self.leds = LEDMAP
		self.logfunc =  logfunc
		self.switchpress = switchpress
		self.resetpress = resetpress
		self.LED_OFF_STATE = 1
		self.LED_ON_STATE = 0
		self.RELAY_ON_STATE = 1
		self.RELAY_OFF_STATE = 0

	def logger(self, msg):
		self.logfunc("%s: %s" % (self.name,msg))
		
	def led_on(self,led):
		self.logger("led %s on" % led)

	def led_off(self,led):
		self.logger("led %s off" % led)

	def relay_on(self):
		self.logger("relay on")
		
	def all_leds_state(self,state):
		if state:
			self.logger("all  leds on")
		else:
			self.logger("all leds off")

	def relay_off(self):
		self.logger("relay off")
		
	def led_blink(self,led, duration=.05):
		self.logger("led %s blink with duration %f" % (led,duration))



def getBestGPIOHandler(type, switchpress=lambda: None,resetpress=lambda: None, logfunc=lambda x: lmbdaproxy(x)):
	ioset = [r00tsIoTNull,r00tsIoTDMX,r00tsIoTRPiGPIO]
	print(type)
	if type == "switch":
		try:
			gapi  = r00tsIoTRPiGPIO(switchpress=switchpress,resetpress=resetpress,logfunc=logfunc)
		except:
			gapi  = r00tsIoTNull(switchpress=switchpress,resetpress=resetpress,logfunc=logfunc)
	elif type == "dmxswitch":
		try:
			gapi  = r00tsIoTDMX(switchpress=switchpress,resetpress=resetpress,logfunc=logfunc)
		except:
			gapi  = r00tsIoTNull(switchpress=switchpress,resetpress=resetpress,logfunc=logfunc)

	return gapi


class r00tsIoTNull(r00tsIoTGPIOBase):
	def __init__(self, switchpress=lambda: None,resetpress=lambda: None, logfunc=lambda x: lmbdaproxy(x)):
		super().__init__(switchpress,resetpress,logfunc)
		self.name = "null_IO_driver"
		
	def led_blink (self,led, duration=.05):
		time.sleep(duration)
		time.sleep(duration)
		super().led_blink(led,duration)

class r00tsIoTRPiGPIO(r00tsIoTGPIOBase):
	def __init__(self, switchpress=lambda: None,resetpress=lambda: None, logfunc=lambda x: lmbdaproxy(x)):
		super().__init__(switchpress,resetpress,logfunc)
		import RPi.GPIO as GPIO
		self.name = "rpi_gpio_driver"
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
	
		for n,l in self.leds.items():
			GPIO.setup(l, GPIO.OUT)
			
		GPIO.setup(IOT_SWITCH_PIN, GPIO.OUT)


	def all_leds_state(self,state):
		for n,b in self.leds.items():
			if state:
				self.led_on(n)
			else:
				self.led_off(n)

	def led_on(self,led):
		GPIO.output(self.leds[led], self.LED_ON_STATE)
		super().led_on(led)
		
	def led_off(self,led):
		GPIO.output(self.leds[led], self.LED_OFF_STATE)
		super().led_off(led)
			
	def relay_on(self):
		GPIO.output(IOT_SWITCH_PIN, self.RELAY_ON_STATE)
		super().relay_on()

	def relay_off(self):
		GPIO.output(IOT_SWITCH_PIN, self.RELAY_OFF_STATE)
		super().relay_off()

	def led_blink (self,led, duration=.05):
		GPIO.output(self.leds[led], self.LED_ON_STATE)
		time.sleep(duration)
		GPIO.output(self.leds[led], self.LED_OFF_STATE)
		time.sleep(duration)
		super().led_blink(led,duration)


class r00tsIoTDMX(r00tsIoTGPIOBase):
	def __init__(self, switchpress=lambda: None,resetpress=lambda: None, logfunc=lambda x: lmbdaproxy(x)):
		super().__init__(switchpress,resetpress,logfunc)
		self.name = "dmx_gpio_driver"







if __name__ == "__main__":
	f = getBestGPIOHandler("switch", logfunc=lambda x: lmbdaproxy(x))
	while(1):
		f.led_blink("status0",)
#		print(f.get_buttonsDict())
