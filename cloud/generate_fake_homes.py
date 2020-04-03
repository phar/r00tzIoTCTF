
from faker import Faker
from faker.providers import internet
from update_switch_status import *	
import random
fake = Faker()


house_rooms = ["Bedroom", "Living Room", "Family Room", "Guest Room", "Kitchen", "Dining Room", "Game Room", "Bathroom", "Basement","Nursery","Home Office","Play Room","Library","Gym","Storage Room","Boiler Room","Server Room"]



for i in range(1000):
	rapi = r00tsIOAAPI()
	fakeuser =   {"username":fake.profile()["username"],"password":fake.password(),"first":fake.first_name(),"last":fake.last_name(),"address":fake.street_address(),"city":fake.city(),"state":fake.state(),"phone": fake.phone_number()}
	print(fakeuser)
	ret = rapi.api_request("register",fakeuser)
	for i in range(random.randint(1,5)):
		p = random.randint(1,5)
		roomstring = ""
		if p == 1:
			roomstring = "%s's " %fake.name()
		roomstring += random.choice(house_rooms)
		print(ret)
		sw = {"house_id":ret["house_id"],"switch_name":roomstring}
		print("\t%s" % sw)
		rapi.api_request("registerSwitch", sw)
