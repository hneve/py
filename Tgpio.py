import wiringpi as wiringpi  
from time import sleep       # allows us a time delay  

LED1 = 22
LED2 = 23
LED3 =24

wiringpi.wiringPiSetupGpio()  
wiringpi.pinMode(LED1, 1)      # sets GPIO 24 to output  
wiringpi.pinMode(LED2, 1)
wiringpi.pinMode(LED3, 1)
wiringpi.digitalWrite(LED1, 0) # sets port 24 to 0 (0V, off)  
wiringpi.digitalWrite(LED2, 0)
wiringpi.digitalWrite(LED3, 0)

wiringpi.pinMode(6, 0)      # sets GPIO 25 to input  
try:  
    while True:  
        wiringpi.digitalWrite(LED1, 1) # switch on LED. Sets port 24 to 1 (3V3, on) 
        sleep(1)
        wiringpi.digitalWrite(LED1, 0) # switch on LED. Sets port 24 to 1 (3V3, on) 
        sleep(1)
        wiringpi.digitalWrite(LED2, 1) # switch on LED. Sets port 24 to 1 (3V3, on) 
        sleep(1)
        wiringpi.digitalWrite(LED2, 0) # switch on LED. Sets port 24 to 1 (3V3, on) 
        sleep(1)
        wiringpi.digitalWrite(LED3, 1) # switch on LED. Sets port 24 to 1 (3V3, on) 
        sleep(1)
        wiringpi.digitalWrite(LED3, 0) # switch on LED. Sets port 24 to 1 (3V3, on) 
        sleep(1)
  
finally:  # when you CTRL+C exit, we clean up  
    wiringpi.digitalWrite(LED1, 0) # sets port 24 to 0 (0V, off)  
    wiringpi.digitalWrite(LED2, 0)
    wiringpi.digitalWrite(LED3, 0)  
    wiringpi.pinMode(LED1, 0)      # sets GPIO 24 to output  
    wiringpi.pinMode(LED2, 0)
    wiringpi.pinMode(LED3, 0)