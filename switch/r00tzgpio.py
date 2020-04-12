import random
import time
#B+ or zero
import syslog


STATUS_LED_0_PIN  = 6
STATUS_LED_1_PIN  = 13
STATUS_LED_2_PIN  = 19
STATUS_LED_3_PIN  = 26
IOT_SWITCH_PIN =  5
INPUT_BUTTON_0_PIN = 20
INPUT_BUTTON_1_PIN = 21


BUTTONMAP = {"factory_reset":INPUT_BUTTON_0_PIN,
			"switch":INPUT_BUTTON_1_PIN}
			
LEDMAP = {	"status0":STATUS_LED_0_PIN,
			"cloudapi":STATUS_LED_1_PIN,
			"firmware":STATUS_LED_2_PIN,
			"relay_led":STATUS_LED_3_PIN}

try:
	import RPi.GPIO as GPIO
	
	LED_OFF_STATE = GPIO.HIGH
	LED_ON_STATE = GPIO.LOW
	RELAY_ON_STATE = GPIO.HIGH
	RELAY_OFF_STATE = GPIO.LOW
	BUTTON_PRESSED_STATE =  0
	BUTTON_RELEASED_STATE = 1

	class r00tsIoTGPIO():
		def __init__(self):
			self.leds = LEDMAP
			self.buttons =BUTTONMAP

			GPIO.setmode(GPIO.BCM)
			GPIO.setwarnings(False)

			for n,l in self.leds.items():
				GPIO.setup(l, GPIO.OUT)
			for n,b in self.buttons.items():
				GPIO.setup(b, GPIO.IN)
			GPIO.setup(IOT_SWITCH_PIN, GPIO.OUT)

		def get_buttons(self):
			buttons = []
			for n,b in self.buttons.items():
				i = GPIO.input(b)
				if i == BUTTON_PRESSED_STATE:
					buttons.append(True)
				else:
					buttons.append(False)
			return buttons

		def get_buttonsDict(self):
			buttons = {}
			for n,b in self.buttons.items():
				i = GPIO.input(b)
				if i == BUTTON_PRESSED_STATE:
					buttons[n] = True
				else:
					buttons[n] = False
			return buttons

		def led_state(self,led,state):
			if state:
				self.led_on(led)
			else:
				self.led_off(led)

		def led_on(self,led):
			GPIO.output(self.leds[led], LED_ON_STATE)

		def led_off(self,led):
			GPIO.output(self.leds[led], LED_OFF_STATE)

		def relay_state(self,state):
			if state:
				self.relay_on(led)
			else:
				self.relay_off(led)
				
		def relay_on(self):
			GPIO.output(self.leds[led], RELAY_ON_STATE)
			
		def relay_off(self):
			GPIO.output(self.leds[led], RELAY_OFF_STATE)

		def led_blink (self,led, duration=.05):
			GPIO.output(self.leds[led], LED_ON_STATE)
			time.sleep(duration)
			GPIO.output(self.leds[led], LED_OFF_STATE)
			time.sleep(duration)
except:

	LED_OFF_STATE = 0
	LED_ON_STATE = 1
	RELAY_ON_STATE = 1
	RELAY_OFF_STATE = 0
	BUTTON_PRESSED_STATE =  0
	BUTTON_RELEASED_STATE = 1

	class r00tsIoTGPIO():
		def __init__(self):
			self.leds = LEDMAP
			self.buttons = BUTTONMAP

		def get_buttons(self):
				buttons = []
				for n,b in self.buttons.items():
					buttons.append(False)
				return buttons

		def get_buttonsDict(self):
			buttons = {}
			for n,b in self.buttons.items():
				buttons[n] = False
			return buttons

		def led_state(self,led,state):
			pass
			
		def led_on(self,led):
			print("led %s on" % led)
			syslog.syslog("led %s on" % led)

		def led_off(self,led):
			print("led %s off" % led)
			syslog.syslog("led %s off" % led)

		def relay_on(self):
			print("relay on")
			syslog.syslog("relay on")

		def relay_off(self):
			print("relay off")
			syslog.syslog("relay off")
			
		def relay_state(self,state):
			pass

		def led_blink(self,led, duration=.05):
			print("led %s blink with duration %f" % (led,duration))
			syslog.syslog("led %s blink with duration %f" % (led,duration))


if __name__ == "__main__":
	f = r00tsIoTGPIO()
	while(1):
		f.blink_led("status0")
		print(f.get_buttonsDict())