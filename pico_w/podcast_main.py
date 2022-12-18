import network
import time
import utime
import ntptime
from machine import I2C,Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import machine
import urequests

# ===========================================
def scankeys():
    key_press = 'X'
    for row in range(4):
        for col in range(4):
            row_pins[row].high()
            key = None
            if col_pins[col].value() == 1:
                key_press = matrix_keys[row][col]
                print(key_press)
                utime.sleep(0.1)      
        row_pins[row].low()
    return key_press

#======= initial lcd =======================
I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()
lcd.move_to(0,0)
lcd.putstr("Initial system")
#======== initial relay =======================
relay_pin = Pin(2,Pin.OUT)
relay_pin.value(1)
switch_open_pin = Pin(5,Pin.IN,Pin.PULL_UP)
#========= initial keypad ============
matrix_keys = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'],['7', '8', '9', 'C'],['*', '0', '#', 'D']]
keypad_rows = [8,9,10,11]
keypad_columns = [12,13,15,16]
col_pins = []
row_pins = []
for x in range(0,4):
    row_pins.append(Pin(keypad_rows[x], Pin.OUT))
    row_pins[x].value(1)
    col_pins.append(Pin(keypad_columns[x], Pin.IN, Pin.PULL_DOWN))
    col_pins[x].value(0)

wlan = network.WLAN(network.STA_IF) #  network.WLAN(network.STA_IF)
wlan.active(True)
# ssid = 'BT-Wifi'
# password = '0820216694'
ssid = 'Praphasawat4'
password = '0659619057'
# ssid = 'Fahmui-IOT'
# password = 'WnHKVxUR'       #=== controller at consulting room ==========
# password = 'azMNb3Ac'       # ======= podcast room ===================
wlan.connect(ssid, password)

max_wait = 30
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    time.sleep(1)

if wlan.status() == 3:
    lcd.clear()
    lcd.putstr('Connect internet')
    lcd.move_to(0,1)
    # local_ip = wlan.ifconfig()[0]
    # lcd.putstr(local_ip)
    lcd.putstr(">>> Complete <<<")
else:
    lcd.clear()
    lcd.putstr("Offline mode")

UTC_OFFSET = 60*60*7

ntp_retry = 10
while True:
    try:
        # print('try ntp')
        ntptime.settime()
        break
    except:
        ntp_retry = ntp_retry -1
        if ntp_retry <= 0:
            machine.reset()

actual_time = time.localtime(time.time() + UTC_OFFSET)
lcd.clear()
date_display = "Date: " + str(actual_time[2]) + '/' + str(actual_time[1]) + '/' + str(actual_time[0])
time_display = "Time: " + "{0:0=2d}".format(actual_time[3]) + ':' + "{0:0=2d}".format(actual_time[4]) + ':' + "{0:0=2d}".format(actual_time[5])
lcd.putstr(date_display)
lcd.move_to(0,1)
lcd.putstr(time_display)

time.sleep(1)
lcd.clear()
#================================
get_code_retry_const = 10
code_link = f'https://script.google.com/macros/s/AKfycbzVBQPT4fRXKyP7R5Y-2lSjVq9AhiIx5JYipqHtV-vpt4TGN47_f8F9TMtWVlE1GB7B/exec'
start_working_hour_const = 7
stop_working_hour_const = 19
#================================
main_state = 0
state_timer = time.ticks_ms()
offline_keycode1 = "*112022#"
offline_keycode2 = "*122022#"
keycode = ""                        # input from keypad
passcode = ""                       # get from server
get_code_retry = 0
wait_off_relay = False
wait_off_relay_timer = time.ticks_ms()
skip_link_server = False
while True:
    if switch_open_pin.value() == 0:
        relay_pin.value(0)
        wait_off_relay = True
        wait_off_relay_timer = time.ticks_ms()

    if wait_off_relay == True:
        if time.ticks_ms() - wait_off_relay_timer >= 3000:
            relay_pin.value(1)
            wait_off_relay = False

    if main_state == 0:
        try:
            if wlan.isconnected():
                lcd.clear()
                lcd.putstr('Link server')
                response = urequests.get(code_link)
                passcode_byte_array = response.content
                response.close()
                if len(passcode_byte_array) >= 11:
                    if passcode_byte_array.decode() == '1234567890':
                        lcd.clear()
                        lcd.move_to(0,0)
                        lcd.putstr('No booking')
                    else:
                        lcd.clear()
                        lcd.move_to(0,0)
                        lcd.putstr('Server problem')
                        main_state = 10
                else:
                    lcd.clear()
                    lcd.putstr('Enter password')
                    passcode = passcode_byte_array.decode()
                    skip_link_server = True
                    main_state = 1
        except:
            main_state = 10
            lcd.putstr('Server problem')
            state_timer = time.ticks_ms()
            if wlan.status() < 0 or wlan.status() >= 3:
                wlan.disconnect()
                wlan.connect(ssid, password)

    elif main_state == 10:
        if time.ticks_ms() - state_timer >= 1000:
            get_code_retry = get_code_retry + 1
            if get_code_retry >= get_code_retry_const:
                lcd.clear()
                lcd.putstr('Offline mode')
                get_code_retry = 0
                main_state = 1
            else:
                main_state = 0

    elif main_state == 1:
        selected_key = scankeys()
        if selected_key >= '#' and selected_key <= 'D':
            keycode = keycode + str(selected_key)
            lcd.move_to(0,1)
            lcd.putstr("                ")
            lcd.move_to(0,1)
            lcd.putstr(keycode)
        if selected_key == '#':
            main_state = 2
        else:
            if len(keycode) >= 9:
                keycode = ""
                main_state = 3

        #========= check time to process ===================
        actual_time = time.localtime(time.time() + UTC_OFFSET)
        present_hour = int(actual_time[3])
        if present_hour >= start_working_hour_const and present_hour <= stop_working_hour_const:
            present_minute = int(actual_time[4])
            if skip_link_server == True:
                if present_minute != 29 or present_minute != 59:
                    skip_link_server = False
            else:
                if present_minute == 29 or present_minute == 59:
                    main_state = 0

    elif main_state == 2:
        if keycode == offline_keycode1:
            main_state = 5
        elif keycode == offline_keycode2:
            main_state = 5
        elif keycode == passcode:
            main_state = 5
        else:
            main_state = 3
        keycode = ""

    elif main_state == 3:
        lcd.clear()
        lcd.putstr("Invalid code")
        state_timer = time.ticks_ms()
        main_state = 4

    elif main_state == 4:
        if time.ticks_ms() - state_timer >= 3000:
            lcd.clear()
            lcd.putstr("Enter password")
            relay_pin.value(1)
            main_state = 1

    elif main_state == 5:
        lcd.clear()
        lcd.putstr("Open")
        state_timer = time.ticks_ms()
        main_state = 4
        relay_pin.value(0)


