"""
Knighit of the MPU6050 accelerometer, 
""" 
from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)

def GetAccelerometerData():
    return sensor.get_accel_data()

def GetGyroData():
    return sensor.get_gyro_data()

def GetMPUdict():
    Adata = GetAccelerometerData()
    Gdata = GetGyroData()
    Astring = { 
        "accx": str(Adata["x"]), 
        "accy": str(Adata["y"]), 
        "accz": str(Adata["z"])
        }
    GString = {
        "gyrx": str(Gdata["x"]), 
        "gyry": str(Gdata["y"]), 
        "gyrz": str(Gdata["z"])
        }
    return {**Astring, **GString }

def Bumped(mpu_data):
    if (float(mpu_data['accx']) > 3):
        #print("x")
        return True

    if (float(mpu_data['accy']) > 3):
        #print("y")
        return True

    if (float(mpu_data['accz']) > 11):
        #print("z")
        return True

    return False



if __name__ == '__main__':
        print( GetMPUdict() )
