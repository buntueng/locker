#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>

//Enter WIFI Credentials
//const char * ssid = "Fahmui-IOT";  // Enter your Wifi Username
//const char * password = "FRCxLtAp";  // D1 password "7Ps7fjhT"
//                                     // D2 password "FRCxLtAp"
const char *ssid     = "Praphasawat4";
const char *password = "0659619057";
String GOOGLE_SCRIPT_ID = "AKfycbyKW0gygJX54QhB6CUA3P0Dc5-MO5pt0HZHd89OIEJr7Z37tjexxicHgMu9pkGuPRkIPw";

//---------------------------------------------------------------------
WiFiClientSecure client;
String message = "Welcome";
void setup() 
{ 
  Serial.begin(115200);
  delay(10);
  //--------------------------------------------
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("OK");
  //--------------------------------------------
}

void loop() 
{
  read_google_sheet();
  delay(300000);
}

void read_google_sheet(void) 
{
   //-----------------------------------------------------------------------------------
   std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);
   client->setInsecure();
   HTTPClient https;
   //String url="https://script.google.com/macros/s/"+GOOGLE_SCRIPT_ID+"/exec?read";
   String url = "https://script.google.com/macros/s/AKfycbyKW0gygJX54QhB6CUA3P0Dc5-MO5pt0HZHd89OIEJr7Z37tjexxicHgMu9pkGuPRkIPw/exec";
   Serial.println("Reading Data From Google Sheet.....");
   https.begin(*client, url.c_str());
   //-----------------------------------------------------------------------------------
   //Removes the error "302 Moved Temporarily Error"
   https.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
   //-----------------------------------------------------------------------------------
   //Get the returning HTTP status code
   int httpCode = https.GET();
   Serial.print("HTTP Status Code: ");
   Serial.println(httpCode);
   //-----------------------------------------------------------------------------------
   if(httpCode <= 0){Serial.println("Error on HTTP request"); https.end(); return;}
   //-----------------------------------------------------------------------------------
   //reading data comming from Google Sheet
   String payload = https.getString();
   Serial.println("Payload: "+payload);
   //-----------------------------------------------------------------------------------
   if(httpCode == 200)
   message= payload;
   //-------------------------------------------------------------------------------------
   https.end();
}
