#! /usr/bin/python3
###################################################################################
# Logging software
#
# Gets gps location and accelerometer data and sends theese to a rest API
#
#
###################################################################################
import json, time, gpsd, requests, socket
from systemd import journal
journal.write("pyMon Starting")
from mpu6050 import mpu6050
import wiringpi as wiringpi 

wiringpi.wiringPiSetupGpio()
LEDnet = 22
LEDgps = 23
LEDsend =24
wiringpi.pinMode(LEDnet, 1)  
wiringpi.pinMode(LEDgps, 1)
wiringpi.pinMode(LEDsend, 1)
wiringpi.digitalWrite(LEDnet, 0)
wiringpi.digitalWrite(LEDgps, 0)
wiringpi.digitalWrite(LEDsend, 0)


sensor = mpu6050(0x68)

report_freq = 60*5  #Seconds between sending report
bump_debounce = 2   #  seconds between bounce alerts
rest_url  = 'https://hneve.com/log/insert.php'
tLedBlink = 1      # Running blink frequency

MPUoffax = 0
MPUoffay = 0
MPUoffaz = 0
MPUoffgx = 0
MPUoffgy = 0
MPUoffgz = 0


###################################################################################
def isConnected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            #print('Closing socket')
            wiringpi.digitalWrite(LEDnet, 1)
            journal.write("pyMon: Internet connection ok")
            sock.close
        return True
    except OSError:  
        pass
    wiringpi.digitalWrite(LEDnet, 0)
    return False
###################################################################################
def getserial():  
  """ 
  Extract serial from cpuinfo file 
  """
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6] == 'Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
  
  return cpuserial[-8:]
###################################################################################
####################################################################################
"""#################################################################################
GPS rutiner
#################################################################################"""
####################################################################################
def gpsInit():
    """
    Starter kobling til gpsd, vil forsøke til koblingen er oppe
    """
    gps_ok = 1
    while gps_ok:
        gps_ok = 0
        try:
            gpsd.connect()      #Koble til gpsd
            journal.write("pyMon: GPS init ok")
        except:
            #print("gpsd error")
            journal.write("pyMon: GPS init Error")
            gps_ok = 1
###################################################################################
def GetGPSPacket(): 
    """ 
    Henter gps pakke fra gpsd, vil forsøke helt til en god pakke (fix > 1) er klar
    """
    while True:
        try:
            Gps_packet = gpsd.get_current()     #Hent gps data
            if Gps_packet.mode > 1:             #Sjekk om fix er minst 2D
                wiringpi.digitalWrite(LEDgps, 1)
                return Gps_packet
        except:                                 #hvis ikke prøv igjen
            journal.write("pyMon: GPS packet exception, retrying in 5 sec")
            wiringpi.digitalWrite(LEDgps, 0)
            time.sleep(5)                     
###################################################################################
def GetGpsDict():                               
    """
    Setter sammen en Dictionary av gps data
    """
    GpsData = GetGPSPacket()
    Gps_d = {
        "time":   str(GpsData.time), 
        "fix":    str(GpsData.mode), 
        "gpslat": str(GpsData.lat), 
        "gpslon": str(GpsData.lon),
        "speed":  str('{:.1f}'.format(GpsData.hspeed * 3.6)) # m/s * 3.6 = km/t
        }

    return Gps_d
###################################################################################
def GpsFence(gps_data,lat_max=60,lat_min=59.5,lon_max=11,lon_min=9.7):
    """
    Forsøk på rudimentær gps gjærde....
    """
    if (float(gps_data['gpslat']) > lat_max ):
        print("lat_max")
        return False
    
    if (float(gps_data['gpslat']) < lat_min ):
        print("lat_min")
        return False
    
    if (float(gps_data['gpslon']) > lon_max):
        print("lon_max")
        return False

    if (float(gps_data['gpslon']) < lon_min):
        print("lon_min")
        return False

    return True
###################################################################################
####################################################################################
"""#################################################################################
  MPU6050 rutiner 
#################################################################################"""
def MPUoffsets():
    tax = 0
    tay = 0
    taz = 0
    tgx = 0
    tgy = 0
    tgz = 0
    L = 100
    while L:
        ''' 
        Hent 100 sample av mpu og gjør gjennomsnitt til offset 
        '''
        tMPUad = sensor.get_accel_data()
        tMPUgd = sensor.get_gyro_data()
        tax += tMPUad["x"]
        tay += tMPUad["y"]
        taz += tMPUad["z"]
        tgx += tMPUgd["x"]
        tgy += tMPUgd["y"]
        tgz += tMPUgd["z"]
        L -= 1

    global MPUoffax
    global MPUoffay 
    global MPUoffaz 
    global MPUoffgx
    global MPUoffgy 
    global MPUoffgz 
    MPUoffax = tax/100
    MPUoffay = tay/100
    MPUoffaz = taz/100
    MPUoffgx = tgx/100
    MPUoffgy = tgy/100
    MPUoffgz = tgz/100
    #print(str(MPUoffax) + ":" + str(MPUoffay) + ":" + str(MPUoffaz))
    #print(str(MPUoffgx) + ":" + str(MPUoffgy) + ":" + str(MPUoffgz))
###################################################################################
def GetMPUdict():
    Adata = sensor.get_accel_data()
    Gdata = sensor.get_gyro_data()
    Astring = { 
        "accx": str('{:.1f}'.format(Adata["x"] - MPUoffax)), 
        "accy": str('{:.1f}'.format(Adata["y"] - MPUoffay)), 
        "accz": str('{:.1f}'.format(Adata["z"] - MPUoffaz))
        }
    GString = {
        "gyrx": str('{:.1f}'.format(Gdata["x"] - MPUoffgx)), 
        "gyry": str('{:.1f}'.format(Gdata["y"] - MPUoffgy)), 
        "gyrz": str('{:.1f}'.format(Gdata["z"] - MPUoffgz))
        }
    return {**Astring, **GString }
###################################################################################
def Bumped(mpu_data):
    if ((float(mpu_data['accx']) - MPUoffax) > 4):
        #print("x")
        return True

    if ((float(mpu_data['accy']) - MPUoffay) > 4):
        #print("y")
        return True

    if ((float(mpu_data['accz']) - MPUoffaz) > 4):
        #print("z")
        return True

    return False
"""#################################################################################
 Hoved rutine
#################################################################################"""

while not isConnected(): 
    pass

gpsInit()
MPUoffsets()

DeviceID = getserial()
send_rest = True
blinkLED = False
last_time_report = time.time()
last_time_blinked = time.time()
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
        if (time.time() >= (last_time_bumped + bump_debounce)):
            log_type = "B"
            send_rest = True
            last_time_bumped = time.time()

    if send_rest:
        payload = {'device': DeviceID, 'type': log_type, **gps_dict, **mpu_dict}
        try:
            r = requests.post(rest_url, data=payload)
            blinkLED = True
            #print(mpu_dict)
        except requests.exceptions.RequestException as e:
            journal.write("pyMon:" + e)
            blinkLED = False
        send_rest = False

    if ((time.time() >= (last_time_blinked + tLedBlink)) and blinkLED):
        wiringpi.digitalWrite(LEDsend, not wiringpi.digitalRead(LEDsend))
        last_time_blinked = time.time()

    if (time.time() >= (last_time_report + report_freq)):
        send_rest = True
        last_time_report = time.time()
