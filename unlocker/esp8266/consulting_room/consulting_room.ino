#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>

#include <NTPClient.h>
#include <WiFiUdp.h>

//Enter WIFI Credentials
//const char * ssid = "Fahmui-IOT";  // Enter your Wifi Username
//const char * password = "FRCxLtAp";  // D1 password "7Ps7fjhT"
//                                     // D2 password "FRCxLtAp"
const char *ssid     = "Praphasawat4";
const char *password = "0659619057";
//---------------------------------------------------------------------
WiFiClientSecure client;
unsigned int main_state = 0;

// NTP parameters
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");
void setup() 
{ 
  Serial.begin(115200);
  delay(10);
  //--------------------------------------------
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  delay(1000);
  timeClient.begin();
  timeClient.setTimeOffset(25200);    // GMT +7 = 7*3600
  WiFi.setAutoReconnect(true);        // reconnect wifi after loss connection
  WiFi.persistent(true);
}

String command = "";
bool execute_cmd = false;
unsigned long ntp_timer = 0;
unsigned int ntp_retry_counter =0;
byte trig_pulse_update_ntp = 0xFF;

void loop() 
{
  // update timer
  if(main_state == 0)
  {
    if(millis()-ntp_timer >= 1000)      // update NTP timer every 1 second
    {
      ntp_timer = millis();
      timeClient.update();;
      if((timeClient.getHours()!=7)&&(timeClient.getMinutes()!=0))
      {
        main_state = 1;
      }
    } 
  }
  else
  { // update ntp at 6 a.m.
    if(millis()-ntp_timer >= 60000)      
    {
      // update NTP timer every day at 6:00 a.m.
      ntp_timer = millis();
      if(timeClient.getHours() == 6)
      {
        trig_pulse_update_ntp = (trig_pulse_update_ntp << 1) + 0;
      }
      else
      {
        trig_pulse_update_ntp = (trig_pulse_update_ntp << 1) + 1;
      }
      if(trig_pulse_update_ntp==0xFE)
      {
        timeClient.update();
      }
    } 
  }
  
  // check serial data
  if(Serial.available())
  {
    char data_in = Serial.read();
    if(data_in == '\n')
    {
      execute_cmd = true;
    }
    else
    {
      command = command + String(data_in);
    }
  }

  if(execute_cmd)
  {
    switch(command[0])
    {
      case 't':     // return current time
      {
        String formattedTime = timeClient.getFormattedTime();
        Serial.println(formattedTime);
        //int currentHour = timeClient.getHours();
        break;
      }
      case 'b':     // check online or offline
      {
        if(WiFi.status() == WL_CONNECTED)
        {
          Serial.println("1");
        }
        else
        {
          Serial.println("0");
        }
        break;
      }
      case 'c':   // check pass code
      {
        break;
      }
      case 's':   // return main state
      {
        Serial.println(main_state);
        break;
      }
      case 'r':   // reset CPU
      {
        ESP.restart();
        break;
      }
      default:
      {
        
      }
    }
    execute_cmd = false;
    command = "";
  }
}

String read_google_sheet(void) 
{
   String resp_message = "GGGGGG";
   //-----------------------------------------------------------------------------------
   std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);
   client->setInsecure();
   HTTPClient https;
   //String url = "https://script.google.com/macros/s/AKfycbyKW0gygJX54QhB6CUA3P0Dc5-MO5pt0HZHd89OIEJr7Z37tjexxicHgMu9pkGuPRkIPw/exec";
   String url = "https://script.google.com/macros/s/AKfycbzVBQPT4fRXKyP7R5Y-2lSjVq9AhiIx5JYipqHtV-vpt4TGN47_f8F9TMtWVlE1GB7B/exec";     // Broadcast
   https.begin(*client, url.c_str());
   //-----------------------------------------------------------------------------------
   //Removes the error "302 Moved Temporarily Error"
   https.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
   //-----------------------------------------------------------------------------------
   //Get the returning HTTP status code
   int httpCode = https.GET();      // if httpCode <=0 error on http request
   if(httpCode == 200)
   {
    String payload = https.getString();
    if(payload.length()==8)
    {
      resp_message= payload;
    }
   }
   https.end();
   return resp_message;
}
