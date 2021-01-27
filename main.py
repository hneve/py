#! /usr/bin/python3
###################################################################################
# Logging software
#
# Gets gps location and accelerometer data and sends theese to a rest API
#
#
###################################################################################
import json
import time
import requests
from systemd import journal

journal.write("pyMon Starting")

from myGps import GetGpsDict, GpsFence, gpsInit
from myMpu import GetMPUdict, Bumped
from mySerial import getshortserial

###################################################################################
VAR_delay = 60*5    #Seconds between sending report
bumb_debounce = 2       # minimum 2 seconds between bounce alerts
rest_url  = 'https://hneve.com/log/insert.php'

DeviceID = getshortserial()
gpsInit()

###################################################################################
send_rest = True
last_time = time.time()
last_time_bumped = time.time()
while True:
    log_type = "r"
    gps_dict = GetGpsDict()
    mpu_dict = GetMPUdict()
    
    if (Bumped(mpu_dict)):
        """
        Om acc data indikerer at boksen er utsatt for støt, skriv til journal og send B merket rapport
        """
        journal.write("pyMon: Bumped")
        if (time.time() >= (last_time_bumped + bumb_debounce)):
            log_type = "B"
            send_rest = True
            last_time_bumped = time.time()

    if send_rest:
        payload = {'device': DeviceID, 'type': log_type, **gps_dict, **mpu_dict}
        try:
            r = requests.post(rest_url, data=payload)
        except requests.exceptions.RequestException as e:
            journal.write("pyMon:" + e)
        send_rest = False




    if (time.time() >= (last_time + VAR_delay)):
        send_rest = True
        last_time = time.time()
