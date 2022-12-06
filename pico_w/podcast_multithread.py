
# import binascii
# import ubinascii
# import socket
# import struct
import time
import network
import urequests
import ntptime
import utime
import _thread
from machine import I2C,Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

#======= initial lcd =======================
I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()
#======== initial relay =======================
relay_pin = Pin(2,Pin.OUT)
relay_pin.value(1)
switch_open_pin = Pin(5,Pin.IN,Pin.PULL_UP)
#========= initial keypad ============
matrix_keys = [['1', '2', '3', 'A'],
               ['4', '5', '6', 'B'],
               ['7', '8', '9', 'C'],
               ['*', '0', '#', 'D']]
keypad_rows = [8,9,10,11]
keypad_columns = [12,13,15,16]
col_pins = []
row_pins = []
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

def get_podcast_passcode():
    keycode = ""
    try:
        response = urequests.get('https://script.google.com/macros/s/AKfycbzVBQPT4fRXKyP7R5Y-2lSjVq9AhiIx5JYipqHtV-vpt4TGN47_f8F9TMtWVlE1GB7B/exec')
        keycode = response.content
        response.close()
    except:
        if wlan.status() < 0 or wlan.status() >= 3:
            wlan.disconnect()
            wlan.connect(ssid, password)
        if wlan.status() == 3:
            keycode = "1"
        else:
            keycode = "2"
    if len(keycode) >= 9:
        keycode = "3"
    return keycode

def get_consult_passcode():
    keycode = ""
    try:
        response = urequests.get('https://script.google.com/macros/s/AKfycbw5XQJ-FJ8ygPKHzFDnXYMIWX73LzbCg0-IWwFXxiXOFFgMTfmlWa2n2mQHbutVqZ_oig/exec')
        keycode = response.content
        response.close()
    except:
        if wlan.status() < 0 or wlan.status() >= 3:
            wlan.disconnect()
            wlan.connect(ssid, password)
        if wlan.status() == 3:
            keycode = "1"
        else:
            keycode = "2"
    if len(keycode) >= 9:
        keycode = "3"
    return keycode
   

def connect_wifi():     # return connection status
    connection_status = False
    wlan.connect(ssid, password)
    max_wait = 30
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(1)
    if wlan.status() == 3:
        connection_status = True
    return connection_status

# ======== global variables ==========
main_state = 0
network_state = 0
passcode = ""               # code from server

UTC_OFFSET = 60*60*7
ssid = 'Fahmui-IOT'
# password = 'WnHKVxUR'       #=== controller at consulting room ==========
# password = 'EDrXvyd4'       # ==== debugging board ==============
password = 'azMNb3Ac'       # ======= podcast room ===================

offline_keycode1 = "*112022#"
offline_keycode2 = "*122022#"

def main_thread():
    global network_state
    global passcode
    global main_state
    keycode = ""

    main_timer = time.ticks_ms()
    switch_open_pin = time.ticks_ms()
    wait_off_relay = False
    while True:
        # ========= process in-room switch ==============
        if switch_open_pin.value() == 0:
            relay_pin.value(0)
            switch_timer = time.ticks_ms()
            wait_off_relay = True

        if wait_off_relay:
            if time.ticks_ms() - switch_timer >= 5000:
                relay_pin.value(1)
                wait_off_relay = False

        # ================== process main state =========
        if main_state == 0:
            keycode = ""
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Linking network")
            main_state = 1

        elif main_state == 1:
            if network_state == 6:          # link success
                lcd.clear()
                lcd.move_to(0,0)
                lcd.putstr("Enter password")
                main_state = 2
            else:
                if time.ticks_ms() - main_timer >= 60000:  # wait at state1 for 1 minute
                    lcd.clear()
                    lcd.move_to(0,0)
                    lcd.putstr("Enter password*")
                    main_state = 2
        elif main_state == 2:
            selected_key = scankeys()
            if selected_key >= '#' and selected_key <= 'D':
                keycode = keycode + str(selected_key)
            if selected_key == '#':
                main_state = 3
            else:
                if len(selected_key) >= 9:
                    keycode = ""
                    main_state = 3

        elif main_state == 3:       # execute passkey
            if keycode == offline_keycode1 or keycode == offline_keycode2 or keycode == passcode:
                relay_pin.value(0)            # open relay
                lcd.move_to(0,1)
                lcd.putstr("Open")
                main_state = 4
            else:
                lcd.move_to(0,1)
                lcd.putstr("Invalid password")
                main_state = 5
            keycode = ""
            main_timer = time.ticks_ms()
        elif main_state == 4:
            if time.ticks_ms() - main_timer >= 5000:
                relay_pin.value(1)
                main_state = 2
                lcd.move_to(0,1)
                lcd.putstr("                ")
        elif main_state == 5:
            if time.ticks_ms() - main_timer >= 2000:
                main_state = 2
                lcd.move_to(0,1)
                lcd.putstr("                ")

def network_thread():
    global network_state
    global passcode
    global wlan
    network_timer = time.ticks_ms()

    while True:
        if network_state == 0:              # try to connect WiFi
            if wlan.status() == 3:
                wlan.disconnect()
            network_state = 1
            network_timer = time.ticks_ms()
        elif network_state == 1:
            if time.ticks_ms() - network_timer >= 1000:
                connection_status = connect_wifi()
                if connection_status == True:
                    network_state = 3
                else:
                    network_timer = time.ticks_ms()
                    network_state = 2
        elif network_state == 2:
            if time.ticks_ms() - network_timer >= 30000:
                network_state = 0

        elif network_state == 3:
            try:
                ntptime.settime()
                network_state = 5
            except:
                network_state = 4
                network_timer = time.ticks_ms()
        elif network_state == 4:
            if time.ticks_ms() - network_timer >= 30000:
                network_state = 3

        elif network_state == 5:        # get first passcode
            present_passcode = get_podcast_passcode()
            if len(present_passcode) > 1:
                passcode = present_passcode
                network_state = 6
            else:
                network_timer = time.ticks_ms()
                network_state = 7
        
        elif network_state == 6:
            actual_time = time.localtime(time.time() + UTC_OFFSET)
            if actual_time[4] == 29 or actual_time[4] == 59:
                present_passcode = get_podcast_passcode()
                if len(present_passcode) > 1:       # someone booking the room and pi pico got passcode
                    passcode = present_passcode
                    network_state = 8
                else:                               # can not retrieve the passcode
                    network_state = 7
                network_timer = time.ticks_ms()
            else:
                if actual_time[3] == 0 and actual_time[4] == 0 and actual_time[5] == 0:         # reset system at midnight
                    reset()

        elif network_state == 7:
            if time.ticks_ms() - network_timer >= 5000:
                network_state = 5
        
        elif network_state == 8:
            if time.ticks_ms() - network_timer >= 60000:
                network_state = 6


# ====================== threads is starting here ===============
main_thread()
_thread.start_new_thread(network_thread, ())