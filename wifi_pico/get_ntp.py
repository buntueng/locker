import ntptime
import time
import network


ssid = 'Fahmui-IOT'
password = 'azMNb3Ac'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

UTC_OFFSET = 7 * 60 * 60
ntptime.settime()
ctime = time.localtime(time.time() + UTC_OFFSET)
print(ctime)

