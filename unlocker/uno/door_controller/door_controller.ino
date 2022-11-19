#include <Wire.h> 
#include<Keypad.h>
#include "LiquidCrystal_I2C.h"
LiquidCrystal_I2C lcd(0x27,16,2);   // 0x27

void show_invalid(void);
void show_open(void);
void show_try_again(void);
void clear_2nd_line(void);

const byte ROWS = 4; //four rows
const byte COLS = 4; //three columns 
char keys[ROWS][COLS] = { 
                         {'1','2','3','A'},
                         {'4','5','6','B'},
                         {'7','8','9','C'},
                         {'*','0','#','D'}};

byte rowPins[ROWS] = {12, 11, 10, 9};
byte colPins[COLS] = {8, 7, 6, 5};

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );

const int relay_pin = 4;///wemos 14
const int switch_pin = 3; //wemos 27

String offline_key = "*112022#";
unsigned int main_state = 0;
String password = "";
bool online_flag = false;
bool hoden_password_flag = false;
unsigned long state_timer = millis();
int password_counter = 0;
int max_length = 4;
String input_password ="";
bool start_saving = false;
bool execute_flag = false;

bool delay_close = false;
unsigned long delay_timer = 0;
bool on_temp_relay = false;
byte switch_state = 0xFF;

bool wait_response = false;
bool resp_complete = false;
String resp_message = "";

unsigned long link_timer = 0;

void setup(){
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  pinMode(7, INPUT_PULLUP);
  pinMode(8, INPUT_PULLUP);

  pinMode(9, INPUT_PULLUP);
  pinMode(10, INPUT_PULLUP);
  pinMode(11, INPUT_PULLUP);
  pinMode(12, INPUT_PULLUP);
  pinMode(relay_pin,OUTPUT);
  pinMode(switch_pin,INPUT_PULLUP);
  digitalWrite(relay_pin,HIGH);       // off relay
  
  Wire.begin();
  delay(1000);
  Serial.begin(115200);
  lcd.begin();
  lcd.backlight();
  lcd.home();
  lcd.print("> Podcast Room <");
  delay(2000);
  lcd.clear();
  lcd.home();
  lcd.print("> Link server <");
  main_state = 0;
  state_timer = millis();
}

//char key = keypad.getKey();
String kep_input = "";
void loop(){
  if(Serial.available())
  {
    char resp_char = Serial.read();
    if(wait_response)
    {
      if(resp_char == '\n')
      {
        wait_response = false;
        resp_complete = true;
      }
      else
      {
        resp_message = resp_message + String(resp_char);
      }
    }
  }
  // check switch inside the room
  switch_state = (switch_state<<1)+ digitalRead(switch_pin);
  if(on_temp_relay)
  {
    if(millis()-delay_timer >= 5000)
    {
      digitalWrite(relay_pin,HIGH);     // off relay
      on_temp_relay = false;
    }
  }
  else
  {
    if(switch_state == 0x00)
    {
      on_temp_relay = true;
      delay_timer = millis();
      digitalWrite(relay_pin,LOW);      // on relay
    }
  }
  // ========================= main state =================
  switch(main_state)
  {
    case 0:
    {
      if((millis()-state_timer)>=1000)
      {
        Serial.flush();
        main_state = 1;
        online_flag = false;
        state_timer = millis();
        link_timer = millis();
      }
      break;
    }
    case 1:
    {
      if(millis()-state_timer >= 1000)
      {
        Serial.print("s");
        Serial.print("\n");
        wait_response = true;
        main_state = 2;
      }
      break;
    }
    case 2:
    {
      if(resp_complete)
      {
        resp_complete = false;
        if(resp_message[0]== '2')
        {
          main_state = 3;
          lcd.home();
          lcd.print(" Enter password ");
        }
        else
        {
          main_state = 1;
          state_timer = millis();
        }
        resp_message = "";
      }
      else
      {
        if(millis()-link_timer>=70000)
          {
            lcd.home();
            lcd.print(" Enter password ");
            main_state = 3;
          }
      }
      break;
    }
    case 3:
    {
      input_password = "";
      password_counter = 0;
      main_state = 4;
      state_timer = millis();
      break;
    }
    case 4:
    {
      char key = keypad.getKey();
      if((key>=35) && key<=68)
      {
        input_password = input_password + String(key);
        lcd.setCursor(0,1);
        lcd.print(input_password);
        if(key == '#')
        {
          execute_flag = true;
        }
        password_counter++;
      }
      if(password_counter >= 9)
      {
        execute_flag = false;
        input_password = "";
        // clear screen
        clear_2nd_line();
        lcd.setCursor(0,1);
        lcd.print("Invalid password");
        main_state = 5;
        state_timer = millis();        
      }
      // ========== check execution =============
      if(execute_flag == true)
      {
        if(input_password.length()==8)
        {
          if(input_password == offline_key)
          {
            show_open();
            digitalWrite(relay_pin,LOW);     // on relay here
            main_state = 6;
            state_timer = millis();
          }
          else
          {
            String cmd_esp8266 = String("p") + input_password;
            Serial.print(cmd_esp8266);
            Serial.print("\n");
            wait_response = true;
            resp_complete = false;
            main_state = 7;
          }
        }
        else
        {
          show_invalid();
          state_timer = millis();
          main_state = 5;
        }
        execute_flag = false;
        input_password = "";
        password_counter = 0;
      }
      break;
    }
    case 5:
    {
      if(millis()-state_timer>=1000)
      {
        clear_2nd_line();
        main_state = 4;
        state_timer = millis();
      }
      break;
    }
    case 6:
    {
      if(millis()-state_timer>=5000)
      {
        digitalWrite(relay_pin,HIGH);     // on relay here
        clear_2nd_line();
        main_state = 3;
      }
      break;
    }
    case 7:   // wait response from p command
    {
      if(resp_complete)
      {
        resp_complete = false;
        clear_2nd_line();
        lcd.setCursor(0,1);
        if(resp_message[0]== '1')
        {
          // open door
          show_open();
          digitalWrite(relay_pin,LOW);
          state_timer = millis();
          main_state = 8;
        }
        else
        {
          // show retry
          digitalWrite(relay_pin,HIGH);
          show_try_again();
          main_state = 5;
          state_timer = millis();
        }
        resp_message = "";
      }
      break;
    }
    case 8:
    {
      // wait 5 seconds then off
      if(millis()-state_timer >= 5000)
      {
        digitalWrite(relay_pin,HIGH);
        main_state = 3;
        clear_2nd_line();
      }
      break;
    }
    default:
    {
      main_state = 0;
    }
  }
}

void show_enter_password(void)
{
  lcd.home();
  lcd.print("Enter password");
}
void show_invalid(void)
{
  lcd.setCursor(0,1);
  lcd.print("Invalid password");
}

void show_open(void)
{
  lcd.setCursor(0,1);
  lcd.print("   open    ");
}

void show_try_again(void)
{
  lcd.setCursor(0,1);
  lcd.print("Please try again");
}

void clear_2nd_line(void)
{
  lcd.setCursor(0,1);
  lcd.print("                ");
}
