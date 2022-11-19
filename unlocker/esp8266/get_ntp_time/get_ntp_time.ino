#include <ESP8266WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

// Replace with your network credentials
//const char *ssid     = "Praphasawat4";
//const char *password = "0659619057";
const char * ssid = "Fahmui-IOT";  // Enter your Wifi Username
const char * password = "7Ps7fjhT";  // D1 password "7Ps7fjhT"

// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");
void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  
  // Connect to Wi-Fi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

// Initialize a NTPClient to get time
  timeClient.begin();
  timeClient.setTimeOffset(25200);          // GMT + 7 = 3600*7
}

void loop() {
  timeClient.update();

  int currentMinute = timeClient.getMinutes();
  Serial.print("Minutes: ");
  Serial.println(currentMinute); 
  delay(2000);
}
