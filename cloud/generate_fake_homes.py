
from faker import Faker
from faker.providers import internet
from update_switch_status import *	
import random
fake = Faker()


for i in range(10000):
	rapi = r00tsIOAAPI()
	fakeuser =   {"username":fake.profile()["username"],"password":fake.password(),"first":fake.first_name(),"last":fake.last_name(),"address":fake.street_address(),"city":fake.city(),"state":fake.state(),"phone": fake.phone_number()}
	print(fakeuser)
	ret = rapi.api_request("register",fakeuser)
	for i in range(random.randint(1,5)):
		sw = {"house_id":ret["house_id"],"switch_id":str(uuid.uuid4())}
		print("\t%s" % sw)
		rapi.api_request("registerSwitch", sw)
