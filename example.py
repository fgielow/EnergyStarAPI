from EnergyStarAPI import Energy_Star_Test_Client
import xml.etree.ElementTree as ET

property_id = "4082666"
#TESTTEST

es_test_client = Energy_Star_Test_Client(username='',password='')

data = es_test_client.get_account_info()

xml_data = ET.fromstring(data)

print(xml_data.tag)