import sys
sys.path.append('../')
sys.path.append('./')
import EnergyStarAPI

import xml.etree.ElementTree as ET

account_file_path = '/opt/EnergyStar/xml-templates/test_account.xml'

account_file = open(account_file_path, "r")
account_file_xml = ET.parse(account_file_path).getroot()

username = account_file_xml[0].text
password = account_file_xml[1].text

es = EnergyStarAPI.EnergyStarTestClient(username, password)



# create main account if not created yet..
try:
	es.create_account(account_file)
except:
	print('Error on account creation. Will continue assuming it failed only because an account already exists for that username.')

# then get info to test
info = es.get_account_info()
print(info)





customer_account_file_path = '/opt/EnergyStar/xml-templates/test_customer_account.xml'
customer_account_file = open(customer_account_file_path, "r")

# create customer account if not created yet..
try:
	es.create_customer_account(customer_account_file)
except:
	print('Error on customer account creation. Will continue assuming it failed only because an account already exists for that username.')


# now get customers


c_info = es.get_customers()
client_id = ET.fromstring(c_info).find('links/link').get('id') # grab the first client id
print(client_id)

print("NOW GET PROPERTIES")
p_info = es.get_properties(client_id)
print(p_info)



print("NOW CREATE")

# let's create a new prop now
property_path = '/opt/EnergyStar/xml-templates/property.xml'
property_file = open(property_path, "r")

p_info = es.create_property(client_id, property_file)
print(p_info)

print("now get ID from this /\\")

prop_id = ET.fromstring(p_info).find('id').text

print("CREATED PROP", prop_id)

print("NOW CREATE METER")

# let's create a new prop now
meter_path = '/opt/EnergyStar/xml-templates/energy_meter.xml'
meter_file = open(meter_path, "r")

p_info = es.create_meter(prop_id, meter_file)
meter_id = ET.fromstring(p_info).find('id').text

print(p_info)
print("CREATED METER %s" % str(meter_id))















# close things







account_file.close()
customer_account_file.close()
property_file.close()


print("DELETE PROP!")
print(es.delete_property(prop_id))