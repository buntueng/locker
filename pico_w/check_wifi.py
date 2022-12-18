import machine
import utime
import _thread
import network
import time
from machine import I2C,Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

thread_lock = _thread.allocate_lock()

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
ssid = 'Praphasawat4'
password = '0659619057'
wlan.connect(ssid, password)

max_wait = 30
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    time.sleep(1)

if wlan.status() == 3:
    lcd.move_to(0,1)
    local_ip = wlan.ifconfig()[0]
    lcd.putstr(local_ip)




def wlan_thread():
    global thread_lock
    global wlan
    wlan_thread_timer = time.ticks_ms()
    while True:
        if time.ticks_ms() - wlan_thread_timer >= 1000:
            wlan_thread_timer = time.ticks_ms()
            thread_lock.acquire()
            print(wlan.status())
            thread_lock.release()


_thread.start_new_thread(wlan_thread, ())

main_state = 0
state_timer = time.ticks_ms()
while True:
    if time.ticks_ms() - state_timer >= 700:
        thread_lock.acquire()
        print('OK')
        thread_lock.release()
        state_timer = time.ticks_ms()
