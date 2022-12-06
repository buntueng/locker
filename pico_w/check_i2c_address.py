import machine
from machine import Pin

i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
devices = i2c.scan()
if len(devices) == 0:
 print("No i2c device !")
else:
 print('i2c devices found:',len(devices))
for device in devices:
 print("Hexa address: ",hex(device))