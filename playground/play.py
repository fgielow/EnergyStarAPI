import os
import sys
import glob
import hashlib
import xml.etree.ElementTree as ET

sys.path.append('../')
sys.path.append('./')
import EnergyStarAPI


def calculate_checksum(filenames):
  hash = hashlib.md5()
  for fn in filenames:
    if os.path.isfile(fn):
      hash.update(open(fn, "rb").read())
  return hash.hexdigest()


class EnergyStarSim:

  base_path = '/opt/EnergyStar/xml-templates/'

  def __del__(self):
    try:
      print("DELETE PROP "+self.property_id+"!")
      print(self.ES.delete_property(self.property_id))
    except:
      self.property_id = None

  def __init__(self, scenario):

    if (scenario == 'common'):
      raise Exception("Scenario cannot be named 'common'")

    self.scenario = scenario


  def connect(self):

    account_file_path = self.base_path +'common/test_account.xml'
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

    customer_account_file_path = self.base_path +'common/test_customer_account.xml'
    customer_account_file = open(customer_account_file_path, "r")

    # create customer account if not created yet..
    try:
      self.ES.create_customer_account(customer_account_file)
    except:
      print('Error on customer account creation. Will continue assuming it failed only because an account already exists for that username.')


    c_info = self.ES.get_customers()

    self.client_id = ET.fromstring(c_info).find('links/link').get('id') # grab the first client id
    print("CUSTOMER ID: " + self.client_id)

  def get_cache_hash(self):
    a = glob.glob(self.get_path('')+'/**/*.xml')
    b = glob.glob(self.get_path('')+'/*.xml')
    c = a + b
    c.sort()
    return calculate_checksum(c)


  def get_path(self, file):
    return self.base_path + self.scenario + '/' + file

  def create_property(self):

    # let's create a new prop now
    property_path = self.get_path('property.xml')
    property_file = open(property_path, "r")

    p_info = self.ES.create_property(self.client_id, property_file)
    self.property_id = ET.fromstring(p_info).find('id').text

    print("CREATED PROPERTY ID: " + self.property_id)

    print("NOT ASSOCIATE WEATHER STATION")
    p_info = self.ES.put_weather_station_association(self.property_id)
    print("GOT " + p_info);



  def create_meter(self):

    # let's create a new prop now
    meter_path = self.get_path('energy_meter.xml')
    meter_file = open(meter_path, "r")

    p_info = self.ES.create_meter(self.property_id, meter_file)
    self.meter_id = ET.fromstring(p_info).find('id').text

    print("CREATED METER ID " + self.meter_id)

    print("NOW SEND METER DATA")

    consumption_path = self.get_path('consumption_data.xml')
    consumption_file = open(consumption_path, "r")

    p_info = self.ES.create_meter_consumption(self.meter_id, consumption_file)

    print("SEND DATA REPLY: "+ p_info)



    print("NOW ASSOCIATE METER")
    p_info = self.ES.associate_meter(self.property_id, self.meter_id)
    print("GOT ANSWER: " + p_info)


  def define_property_uses(self):
    uses_files = glob.glob(self.get_path('prop_uses/*.xml'))
    print("PROPERTY USES:")
    print(uses_files)
    for u_file in uses_files:
      print("configuring usage file: " + u_file)
      usage_file = open(u_file, "r")
      p_info = self.ES.post_usetype_configuration(self.property_id, usage_file)
      print("GOT " + p_info)


  def cache_score(self):
    base_path = '/opt/EnergyStar/cached_scores/'
    h = self.get_cache_hash()
    if (self.e_score and int(self.e_score) > 0):
      f = open(base_path+h, "w")
      f.write(self.e_score)
      f.close()
      print("Updated score for " + h + " to " + self.e_score)

  def get_cached_score(self):
    base_path = '/opt/EnergyStar/cached_scores/'
    h = self.get_cache_hash()
    score = None
    if (os.path.isfile(base_path+h)):
      f = open(base_path+h, "r")
      score = f.read()
      f.close()
      print("Found cached score for " + h + " of " + score)
    return score



  def get_score(self):
    print("NOW TRYING TO GET SCORE.")
    self.e_score = -1

    try:
      p_info = self.ES.get_energy_star_score(self.property_id, 12, 2018)
      self.e_score = ET.fromstring(p_info).find('metric').find('value').text
      print("GOT ENERGY STAR SCORE:" + self.e_score)
    except:
      print("TRY TO GET REASONS FOR NO SCORE!",  sys.exc_info()[0])
      p_info = self.ES.get_reasons_for_no_score(self.property_id, 12, 2018)
      print("GOT ERROR: " + p_info)

    self.cache_score()
    return self.e_score










scenarios = [os.path.basename(x) for x in glob.glob('/opt/EnergyStar/xml-templates/scenarios/*')]

print("SCENARIOS:")
print(scenarios)

scores = {}

for sc in scenarios:
  print("!! INIT - PROCESS SCENARIO " + sc)
  sim = EnergyStarSim('scenarios/'+sc) 
  cached_score = sim.get_cached_score()

  if (cached_score != None):
    scores[sc] = cached_score
  else:
    sim.connect()
    sim.create_property()
    sim.create_meter()
    sim.define_property_uses()
    scores[sc] = sim.get_score()

  del sim


print("\n\n\n\nSUMMARY OF SCORES:")
print(scores)
print("\n\n")









