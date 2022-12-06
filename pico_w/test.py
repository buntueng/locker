import network
import binascii
import time
import ubinascii
import urequests
import socket
import struct
import machine
import ntptime

from machine import I2C,Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()


def get_passcode():
    passcode = ""
    try:
        response = urequests.get('https://script.google.com/macros/s/AKfycbzVBQPT4fRXKyP7R5Y-2lSjVq9AhiIx5JYipqHtV-vpt4TGN47_f8F9TMtWVlE1GB7B/exec')
        # print("sent (" + str(response.status_code) + "), status = " + str(wlan.status()) )
        passcode = response.content
        response.close()
    except:
        # print("could not connect (status =" + str(wlan.status()) + ")")
        if wlan.status() < 0 or wlan.status() >= 3:
            # print("trying to reconnect...")
            wlan.disconnect()
            wlan.connect(ssid, password)
        if wlan.status() == 3:
            passcode = "0001"
        else:
            passcode = "0002"
    if len(passcode) >= 9:
        passcode = "0003"
    return passcode

def scan_ssid():
    networks = wlan.scan() # list with tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden
    networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
    for i,w in enumerate(networks):
        print(i,w[0].decode(),binascii.hexlify(w[1]).decode(),w[2],w[3],w[4],w[5])

def show_mac():
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print(mac)

def connect_wifi():     # return connection status
    connection_status = False
    wlan.connect(ssid, password)
    max_wait = 30
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        lcd.move_to(0,0)
        lcd.putstr('Link network')
        time.sleep(1)
    print(wlan.status())
    if wlan.status() == 3:
        connection_status = True
        lcd.move_to(0,0)
        lcd.putstr('Connected to network')
    return connection_status

main_state = 0
UTC_OFFSET = 60*60*7
ssid = 'Fahmui-IOT'
password = 'WnHKVxUR'       #=== controller at consulting room ==========

wlan = network.WLAN() #  network.WLAN(network.STA_IF)
wlan.active(True)
if wlan.status() == 3:
    wlan.disconnect()
else:
    pass
time.sleep(1)

inloop = True
while inloop:
    if main_state == 0:
        try:
            if connect_wifi() == True:
                main_state = 1
            else:
                main_state = 100
        except:
            main_state = 100
        
    elif main_state == 1:           # update ntp time
        try:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Sync NTP server")
            ntptime.settime()
            main_state = 2
        except:
            main_state = 101
    elif main_state == 2:
        print("state 2")
        actual_time = time.localtime(time.time() + UTC_OFFSET)
        print(len(actual_time))
        lcd.clear()
        lcd.move_to(0,0)
        print(actual_time)
        print(get_passcode())
        main_state = 1000   # exit loop

    #=========== states to handle errors ================
    elif main_state == 100:         # can not connect to wifi
        print("state 100")
        actual_time = time.localtime(time.time() + UTC_OFFSET)
        print(actual_time)
        print(get_passcode())
        main_state = 1000
    elif main_state == 101:         # can not update NTP
        print("can not update ntp")
        main_state = 1000

    elif main_state == 1000:    # exit loop in debug mode
        inloop = False

