#####
#
# Energy Star API
#
#####
import requests
import datetime
import xml.etree.ElementTree as Et



class EnergyStarTestClient(object):
    def __init__(self, username=None, password=None):
        if username is None or password is None:
            raise Exception("Username and Password required")
        self.domain = "https://portfoliomanager.energystar.gov/wstest"
        self.username = username
        self.password = password

    def generic_get(self, path, headers = {}):
        print('GETTING ' + path)
        resource = self.domain + path
        response = requests.get(resource, auth=(self.username, self.password), headers=headers)
        if response.status_code != 200:
            print ('deu ruim')
            return _raise_for_status(response)
        return response.text

    def generic_delete(self, path):
        print('DELETING ' + path)
        resource = self.domain + path
        response = requests.delete(resource, auth=(self.username, self.password))
        if response.status_code != 200:
            print(response.text)
            return _raise_for_status(response)
        return response.text

    def generic_put(self, data, path):
        print('PUTTING ' + path)
        resource = self.domain + path
        headers = {'Content-Type': 'application/xml'}
        response = requests.put(resource, auth=(self.username, self.password), data=data, headers=headers)
        if response.status_code != 200 and response.status_code != 201:
            print(response.text)
            return _raise_for_status(response)
        return response.text

    def generic_post(self, data, path):
        print('POSTING ' + path)
        resource = self.domain + path
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(resource, auth=(self.username, self.password), data=data, headers=headers)
        if response.status_code != 200 and response.status_code != 201:
            print(response.text)
            return _raise_for_status(response)
        return response.text

    def generic_post_file(self, data_file, path):
        if hasattr(data_file, "read"):
            data = data_file.read()
            parsed_data = str(data)
            return self.generic_post(parsed_data, path)
        else:
            print('read file failed')

    def create_account(self, account_file):
        print ('called create_account')
        return self.generic_post_file(account_file, '/account')

    def create_customer_account(self, account_file):
        print ('called create_customer_account')
        return self.generic_post_file(account_file, '/customer')

    def get_customers(self):
        print ('called get_customers')
        return self.generic_get("/customer/list")

    def delete_property(self, property_id):
        print ('called delete_property')
        return self.generic_delete("/property/%s" % str(property_id))

    def create_property(self, account_id, property_file):
        print ('called create_property')
        return self.generic_post_file(property_file, "/account/%s/property" % str(account_id))

    def create_meter(self, property_id, meter_file):
        print ('called create_meter')
        return self.generic_post_file(meter_file, "/property/%s/meter" % str(property_id))

    def associate_meter(self, property_id, meter_id):
        print ('called associate_meter')
        return self.generic_post({}, "/association/property/%s/meter/%s" % (str(property_id), str(meter_id)))

    def create_meter_consumption(self, meter_id, consumption_file):
        print ('called create_meter_consumption')
        return self.generic_post_file(consumption_file, "/meter/%s/consumptionData" % str(meter_id))

    def get_properties(self, account_id):
        print ('called get_properties')
        return self.generic_get("/account/%s/property/list" % str(account_id))

    def get_reasons_for_no_score(self, property_id, ending_month, ending_year):
        print ('called get_reasons_for_no_score')
        path = "/property/%s/reasonsForNoScore?year=%s&month=%s" % ( str(property_id), str(ending_year), str(ending_month) )
        return self.generic_get(path)

    def get_energy_star_score(self, property_id, ending_month, ending_year):
        print ('called get_energy_star_score')
        path = "/property/%s/metrics?year=%s&month=%s&measurementSystem=%s" % ( str(property_id), str(ending_year), str(ending_month), 'METRIC' )
        headers = {
            'PM-Metrics': 'score'
        }
        return self.generic_get(path, headers)

    def post_usetype_configuration(self, property_id, usage_type_file):
        print ('called post_usetype_configuration')
        return self.generic_post_file(usage_type_file, "/property/%s/propertyUse" % str(property_id))


    def get_account_info(self):
        print ('called get_account_info')
        return self.generic_get("/account")

    def get_associated_meter_list(self, prop_id):
        print ('called get_meter_list')
        return self.generic_get("/association/property/%s/meter" % str(prop_id))

    def get_meter_list(self, prop_id):
        print ('called get_meter_list')
        return self.generic_get("/property/%s/meter/list" % str(prop_id))

    def put_weather_station_association(self, property_id):
        print ('called put_weather_station_association')
        # ASSOCIATING FIXED:
        #   <station id="31400" country="GB" countryName="United Kingdom" stationName="GLASGOW AIRPORT"/>
        path="/property/%s/internationalWeatherStation/%s" % ( str(property_id), str(31400))
        return self.generic_put({}, path)

    def get_weather_stations(self):
        print ('called get_weather_stations')
        return self.generic_get("/property/internationalWeatherStation/list?page=1&country=GB")


class EnergyStarClient(object):
    def __init__(self, username=None, password=None):
        if username is None or password is None:
            raise Exception("Username and Password required")
        self.domain = "https://portfoliomanager.energystar.gov/ws"
        self.username = username
        self.password = password

    def get_account_info(self):
        resource = self.domain + "/account"
        response = requests.get(resource, auth=(self.username, self.password))

        if response.status_code != 200:
            return _raise_for_status(response)
        return response.text

    def get_meter_list(self, prop_id):
        resource = self.domain + '/association/property/%s/meter' % str(prop_id)
        response = requests.get(resource, auth=(self.username, self.password))

        if response.status_code != 200:
            return _raise_for_status(response)

        data = response.text
        meters = dict()

        root = Et.fromstring(data)

        for e in root.iter("*"):
            if e.tag == "meterId":
                meter_type = self.get_meter_type(e.text)
                meters[e.text] = meter_type

        return meters

    def get_meter_type(self, meter_id):
        resource = self.domain + '/meter/%s' % str(meter_id)

        response = requests.get(resource, auth=(self.username, self.password))
        data = response.text

        root = Et.fromstring(data)
        meter_type = ''
        for e in root.iter("*"):
            if e.tag == "type":
                meter_type = e.text

        return meter_type

    def get_building_info(self, prop_id):
        resource = self.domain + '/building/%s' % str(prop_id)
        response = requests.get(resource, auth=(self.username, self.password))

        if response.status_code != 200:
            return _raise_for_status(response)
        return response.text

    def get_usage_data(self, meter_id, months_ago):
        # Get date in YYYY-MM-DD format from months ago
        date_format = '%Y-%m-%d'
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(days=months_ago * 30)
        start_date = datetime.datetime.strftime(start_date, date_format)
        resource = self.domain + '/meter/%s/consumptionData' % str(meter_id)

        usage = []

        url = resource + '?page=1&startDate=' + start_date
        page = 1
        while url:
            print(url)
            print("Getting data from page " + str(page))
            page += 1

            response = requests.get(url, auth=(self.username, self.password))

            if response.status_code != 200:
                print(response.status_code, response.reason)
                break
            # Set URL to none to stop loop if no more links
            url = None

            data = response.text
            root = Et.fromstring(data)
            for element in root.findall("meterConsumption"):
                month_data = dict()
                # Get the usage data
                month_data[element.find("endDate").text] = float(element.find("usage").text)
                usage.append(month_data)

            # Get the next URL
            for element in root.find("links"):
                for link in element.findall("link"):
                    if link.get("linkDescription") == "next page":
                        url = self.domain + link.get("link")
        # Return the usage for the time period
        return usage

    def get_cost_data(self, meter_id, months_ago):
        # Get date in YYYY-MM-DD format from months ago
        date_format = '%Y-%m-%d'
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(days=months_ago * 30)
        start_date = datetime.datetime.strftime(start_date, date_format)
        resource = self.domain + '/meter/%s/consumptionData' % str(meter_id)

        cost = []

        url = resource + '?page=1&startDate=' + start_date
        page = 1
        while url:
            print(url)
            print("Getting data from page " + str(page))
            page += 1

            response = requests.get(url, auth=(self.username, self.password))

            if response.status_code != 200:
                print(response.status_code, response.reason)
                break
            # Set URL to none to stop loop if no more links
            url = None

            data = response.text
            root = Et.fromstring(data)
            for element in root.findall("meterConsumption"):
                month_data = dict()
                # Get the cost data
                month_data[element.find("endDate").text] = float(element.find("cost").text)
                # append to cost
                cost.append(month_data)

            # Get the next URL
            for element in root.find("links"):
                for link in element.findall("link"):
                    if link.get("linkDescription") == "next page":
                        url = self.domain + link.get("link")
        # Return the cost for the time period
        return cost

    def get_usage_and_cost(self, meter_id, months_ago):
        # Get date in YYYY-MM-DD format from months ago
        date_format = '%Y-%m-%d'
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(days=months_ago * 30)
        start_date = datetime.datetime.strftime(start_date, date_format)
        resource = self.domain + '/meter/%s/consumptionData' % str(meter_id)

        usage_and_cost = []

        url = resource + '?page=1&startDate=' + start_date

        while url:
            print(url)

            response = requests.get(url, auth=(self.username, self.password))

            if response.status_code != 200:
                print(response.status_code, response.reason)
                break
            # Set URL to none to stop loop if no more links
            url = None

            data = response.text
            root = Et.fromstring(data)
            for element in root.findall("meterConsumption"):
                month_data = dict()
                # Get the usage and cost data
                usage_cost = [float(element.find("usage").text), float(element.find("cost").text)]

                # match with the date
                month_data[element.find("endDate").text] = usage_cost

                # append to usage
                usage_and_cost.append(month_data)

            # Get the next URL
            for element in root.find("links"):
                for link in element.findall("link"):
                    if link.get("linkDescription") == "next page":
                        url = self.domain + link.get("link")
        # Return the cost for the time period
        return usage_and_cost


def _raise_for_status(response):
    """
    Custom raise_for_status with more appropriate error message.
    """
    http_error_msg = ""

    if 400 <= response.status_code < 500:
        http_error_msg = "{0} Client Error: {1}".format(response.status_code,
                                                        response.reason)

    elif 500 <= response.status_code < 600:
        http_error_msg = "{0} Server Error: {1}".format(response.status_code,
                                                        response.reason)

    if http_error_msg:
        try:
            more_info = response.json().get("message")
        except ValueError:
            more_info = None
        if more_info and more_info.lower() != response.reason.lower():
            http_error_msg += ".\n\t{0}".format(more_info)
        raise requests.exceptions.HTTPError(http_error_msg, response=response)




def __main__():
    print('oie')