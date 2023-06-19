
import sys
import requests
import json
from requests.auth import HTTPBasicAuth
import os
import csv
import datetime


num_args = len(sys.argv)

if num_args < 3:
    print("Usage: python SunSynkTool.py [username] [password] [region]...")
    sys.exit(1)

# Access individual command-line arguments
my_user_email = sys.argv[1]
my_user_password = sys.argv[2]
my_region = int(sys.argv[3])

global region_url

if my_region == 1:
    region_url = 'pv.inteless.com'
    
if my_region == 2:
    region_url = 'api.sunsynk.net'



loginurl = (f'https://{region_url}/oauth/token/')


# API call to get realtime inverter related information
plant_id_endpoint = (f'https://{region_url}/api/v1/plants?page=1&limit=10&name=&status=')



global load_shedding
load_shedding = False
global pvs_power
global battery_soc
global grids_voltage
global grids_power
global load

def my_bearer_token():

    headers = {
    'Content-type':'application/json', 
    'Accept':'application/json'
    }

    payload = {
        "username": my_user_email,
        "password": my_user_password,
        "grant_type":"password",
        "client_id":"csp-web",
        "source":"sunsynk",
        "areaCode":"sunsynk"
        }

    
    raw_data = requests.post(loginurl, json=payload, headers=headers).json()

    print(raw_data)

    # Your access token extracted from response
    my_access_token = raw_data["data"]["access_token"]
    global the_bearer_token_string
    the_bearer_token_string = ('Bearer '+ my_access_token)
    print('****************************************************')
    print('Your access token is: ' + my_access_token)
    return my_access_token


def get_plant_id():
    headers_and_token = {
    'Content-type':'application/json', 
    'Accept':'application/json',
    'Authorization': the_bearer_token_string
    }
    r = requests.get(plant_id_endpoint, headers=headers_and_token)
    data_response = r.json()
    #print(data_response)

    plant_id_and_pac = data_response['data']['infos']
    your_plant_id = ""
    for d in plant_id_and_pac:
        your_plant_id = d['id']

    if(your_plant_id):
        return your_plant_id
    else:
        print("Error: Plant_id not found")
        sys.exit()




def get_inverters():

    inverters_url = f'https://{region_url}/api/v1/inverters?page=1&limit=10&total=0&status=-1&sn=&plantId=&type=-2&softVer=&hmiVer=&agentCompanyId=-1&gsn='


    headers_and_token = {
    'Content-type':'application/json', 
    'Accept':'application/json',
    'Authorization': the_bearer_token_string
    }
    r = requests.get(inverters_url, headers=headers_and_token)
    data_response = r.json()
  

    inv_data = data_response['data']['infos']

    inverters = []
    for inverter in inv_data:
        inverter_id = inverter['sn']
        inverters.append(inverter_id)
        #print(inverter_id)
    return(inverters)


def get_inverter_input_data(inverter_id):


    inverters_url = f'https://{region_url}/api/v1/inverter/' + str(inverter_id) + '/realtime/input'
    headers_and_token = {
    'Content-type':'application/json', 
    'Accept':'application/json',
    'Authorization': the_bearer_token_string
    }
    r = requests.get(inverters_url, headers=headers_and_token)
    data_response = r.json()


    pvIV = data_response['data']['pvIV']

    print('PV/INPUT Data for Inverter: '  + inverter_id)
    print('****************************************************')
    
    for pvs in pvIV:
        #print(pvs)
        pvNo = pvs['pvNo']
        vpv = pvs['vpv']
        ipv = pvs['ipv']
        ppv = pvs['ppv']
        todayPv = pvs['todayPv']

        print(' pvNo: ' + str(pvNo))
        print('     vpv: ' + str(vpv))
        print('     ipv: ' + str(ipv))
        print('     ppv: ' + str(ppv))
        print('     todayPv: ' + str(todayPv))

       




def get_inverter_grid_data(inverter_id):

    inverters_url = f'https://{region_url}/api/v1/inverter/grid/' + str(inverter_id) + '/realtime?sn=' + str(inverter_id)


    headers_and_token = {
    'Content-type':'application/json', 
    'Accept':'application/json',
    'Authorization': the_bearer_token_string
    }
    r = requests.get(inverters_url, headers=headers_and_token)
    data_response = r.json()



    
    vip = data_response['data']['vip']
 
    for grid_data in vip:

        grid_voltage = grid_data['volt']
        grid_current = grid_data['current']
        grid_power = grid_data['power']
        global grids_power
        grids_power = grid_power
        #print(inverter_id)
        print('Grid Data for Inverter: '  + inverter_id)
        print('****************************************************')
        print('GridVoltage: ' + str(grid_voltage) + "V")
        print('GridCurrent: ' + str(grid_current) + "A")
        print('GridPower: ' + str(grid_power) + "W")
       

        global grids_voltage
        grids_voltage = grid_voltage


        
    

def my_current_usage(plant_id):


    current_inverter_flow = f'https://{region_url}/api/v1/plant/energy/'+ str(plant_id) +'/flow'



    headers_and_token = {
    'Content-type':'application/json', 
    'Accept':'application/json',
    'Authorization': the_bearer_token_string
    }
    r = requests.get(current_inverter_flow, headers=headers_and_token)
    data_response = r.json()
  

    
    print('****************************************************')
    d = data_response['data']
    
    pvPower = d['pvPower']
    battPower = d['battPower']
    gridOrMeterPower = d['gridOrMeterPower']
    loadOrEpsPower = d['loadOrEpsPower']
    genPower = d['genPower']
    minPower = d['minPower']
    soc = d['soc']

    print('Your plant id is: ' + str(plant_id))
    print('****************************************************')
    print('PVPower: ' + str(pvPower) + "W")
    print('battPower:' + str(battPower) + "W")
    print('gridPower:' + str(gridOrMeterPower) + "W")
    print('load:' + str(loadOrEpsPower) + "W")
    print('Your SOC: ' + str(soc) +'%')

    print('****************************************************')



    global pvs_power
    pvs_power = pvPower
    global battery_soc
    battery_soc = soc
    global load
    load = loadOrEpsPower
    


if __name__ == "__main__":
    my_bearer_token()
    plant_id = get_plant_id()
    print(plant_id)
    my_current_usage(plant_id)

    inverters = get_inverters()

    for inv in inverters:
        get_inverter_grid_data(inv)
        get_inverter_input_data(inv)



    #Decision Logic
    print("PV: " + str(pvs_power) + "W")
    print("SOC: " + str(battery_soc) + "%")
    print("GRIDS_VOLTAGE: " + str(grids_voltage) + "W")
    if(float(grids_voltage) < 100):
        load_shedding = True
    
    print("LOAD SHEDDING: " + str(load_shedding))

    # Now let's write this data to a CSV file
    """
    filename = 'solar_data_log.csv'
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:

        writer = csv.writer(f)

        headers = ['timestamp', 'pvs_power', 'grids_power', 'load', 'battery_soc', 'load_shedding']
        
        # If file does not exist, write headers
        if not file_exists:
            writer.writerow(headers)


        writer.writerow([datetime.datetime.now(), pvs_power,  grids_power, load, battery_soc, load_shedding])
    """


'''
    if(load_shedding == False):

            ifttt_url = 'https://maker.ifttt.com/trigger/power_on_plugs/json/with/key/zzzz'
            headers = {'Content-Type': 'application/json'}
            r = requests.post(ifttt_url, json={"event": "No LoadShedding Detected"})
            print(f"Status Code: {r.status_code}, Response: {r.text}")

    if(load_shedding == True):
            ifttt_url = 'https://maker.ifttt.com/trigger/power_off_plugs/json/with/key/xxxxx'
            headers = {'Content-Type': 'application/json'}
            r = requests.post(ifttt_url, json={"event": "No LoadShedding Detected"})
            print(f"Status Code: {r.status_code}, Response: {r.text}")
    
'''

