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

# create if not created yet..
try:
	es.create_account(account_file)
except:
	print('Error on account creation. Will continue assuming it failed only because an account already exists for that username.')

# then get info to test
info = es.get_account_info()
print(info)





account_file.close()