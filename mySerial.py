"""
Enkel mååte å hente "serienummeret" på cpu
Fin måte å skille mellom enheter
"""

def getserial():
    """ Extract serial from cpuinfo file """
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6] == 'Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
 
  return cpuserial

def getshortserial():
    """ Cut last 8 characters from serial """
    return getserial()[-8:]

if __name__ == '__main__':  #hvis filen kjøres direkte ....
    print(getserial())
    print(getshortserial())