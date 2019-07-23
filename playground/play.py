import sys
sys.path.append('../')
sys.path.append('./')
import EnergyStarAPI

import xml.etree.ElementTree as ET


class EnergyStarSim:

  def __del__(self):
    print("DELETE PROP "+self.property_id+"!")
    print(self.ES.delete_property(self.property_id))

  def __init__(self):
    account_file_path = '/opt/EnergyStar/xml-templates/test_account.xml'

    account_file = open(account_file_path, "r")
    account_file_xml = ET.parse(account_file_path).getroot()

    username = account_file_xml[0].text
    password = account_file_xml[1].text

    self.ES = EnergyStarAPI.EnergyStarTestClient(username, password)

    # create main account if not created yet..
    try:
      self.ES.create_account(account_file)
    except:
      print('Error on account creation. Will continue assuming it failed only because an account already exists for that username.')

    customer_account_file_path = '/opt/EnergyStar/xml-templates/test_customer_account.xml'
    customer_account_file = open(customer_account_file_path, "r")

    # create customer account if not created yet..
    try:
      self.ES.create_customer_account(customer_account_file)
    except:
      print('Error on customer account creation. Will continue assuming it failed only because an account already exists for that username.')


    c_info = self.ES.get_customers()

    self.client_id = ET.fromstring(c_info).find('links/link').get('id') # grab the first client id
    print("CUSTOMER ID: " + self.client_id)



  def create_property(self):

    # let's create a new prop now
    property_path = '/opt/EnergyStar/xml-templates/property.xml'
    property_file = open(property_path, "r")

    p_info = self.ES.create_property(self.client_id, property_file)
    self.property_id = ET.fromstring(p_info).find('id').text

    print("CREATED PROPERTY ID: " + self.property_id)

    print("NOT ASSOCIATE WEATHER STATION")
    p_info = self.ES.put_weather_station_association(self.property_id)
    print("GOT " + p_info);



  def create_meter(self):

    # let's create a new prop now
    meter_path = '/opt/EnergyStar/xml-templates/energy_meter.xml'
    meter_file = open(meter_path, "r")

    p_info = self.ES.create_meter(self.property_id, meter_file)
    self.meter_id = ET.fromstring(p_info).find('id').text

    print("CREATED METER ID " + self.meter_id)

    print("NOW SEND METER DATA")

    consumption_path = '/opt/EnergyStar/xml-templates/consumption_data.xml'
    consumption_file = open(consumption_path, "r")

    p_info = self.ES.create_meter_consumption(self.meter_id, consumption_file)

    print("SEND DATA REPLY: "+ p_info)



    print("NOW ASSOCIATE METER")
    p_info = self.ES.associate_meter(self.property_id, self.meter_id)
    print("GOT ANSWER: " + p_info)


  def define_property_uses(self):
    print("DEFINE OFFICE NOW")
    office_path = '/opt/EnergyStar/xml-templates/office_data.xml'
    office_file = open(office_path, "r")
    p_info = self.ES.post_usetype_configuration(self.property_id, office_file)
    print("GOT " + p_info)

    print("DEFINE PARKING NOW")
    parking_path = '/opt/EnergyStar/xml-templates/parking_data.xml'
    parking_file = open(parking_path, "r")
    p_info = self.ES.post_usetype_configuration(self.property_id, parking_file)
    print("GOT " + p_info)


  def get_score(self):
    print("NOW TRYING TO GET SCORE.")
    try:
      p_info = self.ES.get_energy_star_score(self.property_id, 6, 2019)
      self.e_score = ET.fromstring(p_info).find('metric').find('value').text
      print("GOT " + self.e_score)
    except:
      print("TRY TO GET REASONS FOR NO SCORE!")
      p_info = self.ES.get_reasons_for_no_score(self.property_id, 6, 2019)
      print("GOT " + p_info)




sim = EnergyStarSim() 
sim.create_property()
sim.create_meter()
sim.define_property_uses()
sim.get_score()

del sim



