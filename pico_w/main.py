import network
import binascii
import time
import ubinascii
import urequests
import socket
import struct
import machine
import ntptime
import utime

from machine import I2C,Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

#======= lcd =======================
I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()

relay_pin = Pin(2,Pin.OUT)
relay_pin.value(1)
switch_open_pin = Pin(5,Pin.IN,Pin.PULL_UP)

main_timer = time.ticks_ms()
#========= keypad ============
# CONSTANTS
matrix_keys = [['1', '2', '3', 'A'],
               ['4', '5', '6', 'B'],
               ['7', '8', '9', 'C'],
               ['*', '0', '#', 'D']]
keypad_rows = [8,9,10,11]
keypad_columns = [12,13,15,16]
col_pins = []
row_pins = []

# Loop to assign GPIO pins and setup input and outputs
for x in range(0,4):
    row_pins.append(Pin(keypad_rows[x], Pin.OUT))
    row_pins[x].value(1)
    col_pins.append(Pin(keypad_columns[x], Pin.IN, Pin.PULL_DOWN))
    col_pins[x].value(0)

def scankeys():
    key_press = 'X'
    for row in range(4):
        for col in range(4):
            row_pins[row].high()
            key = None
            
            if col_pins[col].value() == 1:
                key_press = matrix_keys[row][col]
                print(key_press)
                utime.sleep(0.3)
                    
        row_pins[row].low()
    return key_press


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
    max_wait = 20
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

execute = False
keycode = ""
keyupdate = False
main_state = 0
UTC_OFFSET = 60*60*7
ssid = 'Fahmui-IOT'
password = 'WnHKVxUR'       #=== controller at consulting room ==========
# password = 'EDrXvyd4'       # ==== debugging board ==============
# password = 'azMNb3Ac'       # ======= podcast room ===================


wlan = network.WLAN() #  network.WLAN(network.STA_IF)
wlan.active(True)
if wlan.status() == 3:
    wlan.disconnect()
else:
    pass
time.sleep(1)
print(wlan.status())

switch_timer = time.ticks_ms()
wait_off_relay = False
inloop = True
while inloop:
    if switch_open_pin.value() == 0:
        relay_pin.value(0)
        switch_timer = time.ticks_ms()
        wait_off_relay = True

    if wait_off_relay == True:
        if time.ticks_ms() - switch_timer >= 5000:
            wait_off_relay = False
            relay_pin.value(1)

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
        lcd.putstr("Enter password")
        main_state = 3

    elif main_state == 3:
        print("state3")
        selected_key = scankeys()
        if(selected_key <= 'D'):
            keyupdate = True
            keycode = keycode + str(selected_key)
            if selected_key == '#':
                execute = True

        if keyupdate == True:
            lcd.clear()
            lcd.move_to(0,1)
            lcd.putstr(keycode)
            keyupdate = False

        if execute == True:
            if keycode == "*112022#":
                lcd.clear()
                lcd.move_to(0,0)
                lcd.putstr("Open")
                relay_pin.value(0)
                main_timer = time.ticks_ms()
                main_state = 4

            else:
                lcd.clear()
                lcd.move_to(0,0)
                lcd.putstr("Enter key")
            keycode = ""
            execute = False
        else:
            if(len(keycode)>8):
                lcd.clear()
                lcd.move_to(0,0)
                lcd.putstr("Invalid password")
                keycode = ""
        
            
    elif main_state == 4:           # wait open
        if (time.ticks_ms() - main_timer) >= 5000:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Enter key") 
            main_state = 3
            relay_pin.value(1)
            

            
        

    #=========== states to handle errors ================
    elif main_state == 100:         # can not connect to wifi
        print("state 100")
        actual_time = time.localtime(time.time() + UTC_OFFSET)
        print(actual_time)
        print(get_passcode())
        main_state = 1000
    elif main_state == 101:         # can not update NTP
        print("can not update ntp")
        main_state = 2
        actual_time = time.localtime(time.time() + UTC_OFFSET)
        print(actual_time)

    elif main_state == 1000:    # exit loop in debug mode
        inloop = False

