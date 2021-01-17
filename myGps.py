"""
Gps fikse modul  
Note: 
pip3 install gpsd-py3 :: https://github.com/MartijnBraam/gpsd-py3/
gpsd daemon må kjøre! 
-sudo apt-get install gpsd gpsd-clients python-gps
-sudo systemctl stop gpsd.socket
-sudo systemctl disable gpsd.socket
-sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
"""
from systemd import journal
import gpsd, time, sys

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
            journal.write("myGps: GPS connected")
        except:
            #print("gpsd error")
            journal.write("myGps: No GPS")
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
                return Gps_packet
        except:                                 #hvis ikke prøv igjen
            journal.write("myGps: Bad gps packet, retrying in 5 sec")
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
###################################################################################
if __name__ == '__main__':  
    """
    Hvis filen kjøres direkte print data
    """
    gpsInit()    
    print( GetGpsDict() )
