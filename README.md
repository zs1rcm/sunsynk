# sunsynk script 

This script queries Sunsynk api for inverter and pv data:

Usage: python3 SunSynkToolf.py <username> <password> <region>
  

##########################################################################################  

  I use this as a ghetto loadshedding detector, eg:   
  
 <code>
  if(float(grids_voltage) < 100):
        load_shedding = True
 </code>
   
                                                                             
Then I post to iftt webhooks to control some internal scenes in smartlife for high load devices like pool pumps, dryers etc. 
                                 
Eg:
<code>                                 
 if(load_shedding == True):
            ifttt_url = 'https://maker.ifttt.com/trigger/power_off_plugs/json/with/key/xxxxx'
            headers = {'Content-Type': 'application/json'}
            r = requests.post(ifttt_url, json={"event": "No LoadShedding Detected"})
            print(f"Status Code: {r.status_code}, Response: {r.text}")
</code>
