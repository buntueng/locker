#include <Wire.h> 
#include<Keypad.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x3f,16,2);

void show_try_to_connect_server(void);
void show_offline(void);
void show_online(void);
void show_invalid(void);
void show_open(void);
void show_try_again(void);
void clear_2nd_line(void);

const byte ROWS = 4; //four rows
const byte COLS = 3; //three columns
char keys[ROWS][COLS] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};
byte rowPins[ROWS] = {23, 5, 13, 12}; //connect to the row pinouts of the keypad
byte colPins[COLS] = {17, 25, 26}; //connect to the column pinouts of the keypad

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );

String offline_key = "2022";
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

void setup(){
  Wire.begin();
  delay(1000);
  Serial.begin(9600);
  lcd.begin();
  lcd.backlight();
  lcd.home();
  lcd.print("GigGox man");
  delay(2000);
  lcd.clear();
  lcd.home();
  main_state = 0;
  state_timer = millis();

  Serial.print("Running");
}

//char key = keypad.getKey();
void loop(){
  switch(main_state)
  {
    case 0:
    {
      show_try_to_connect_server();
      if((millis()-state_timer)>=1000)
      {
        main_state = 1;
        online_flag = false;
      }
      break;
    }
    case 1:
    {
      // in offline mode
      if(online_flag == false)
      {
        show_offline();
        main_state = 2;
        input_password ="";
      }
      else
      {
        show_online();
        main_state = 3;
        input_password ="";
      }
      break;
    }
    case 2:
    {
      char key = keypad.getKey();
      if(key >=35 && key <= 57)
      {
        if(start_saving == false)
        {
          if(key == '*')
          {
            password_counter = 0;
            input_password ="";
            start_saving = true;
          }
        }
        else
        {
          if(key == '#')
          {
            execute_flag = true;
          }
          else
          {
            if(key == '*')
            {
              password_counter = 0;
              input_password ="";
              start_saving = true;
            }
            else
            {
              input_password = input_password + String(key);
              password_counter = password_counter + 1;
            }
          }
        }
        // ========== check execution =============
        if(execute_flag == true)
        {
          if(input_password == offline_key)
          {
            show_open();
            // on relay here
            main_state = 4;
            state_timer = millis();
          }
          else
          {
            show_try_again();
            state_timer = millis();
            main_state = 3;
          }
          execute_flag = false;
          input_password = "";
          password_counter = 0;
        }
        // ========== check password length =======
        if(password_counter>max_length)
        {
          password_counter = 0;
          input_password = "";
          show_invalid();
          main_state = 3;
          state_timer = millis();
        }
      }
      break;
    }
    case 3:     // re entry password  from invalid
    {
      if((millis()-state_timer)>=1000)
      {
        main_state = 2;
        clear_2nd_line();
      }
      break;
    }
    case 4:     // from open door
    {
      if((millis()-state_timer)>=10000)
      {
        // off relay
        main_state = 2;
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


void show_try_to_connect_server(void)
{
  lcd.home();
  lcd.print("try to connect server");
}

void show_offline(void)
{
  lcd.clear();
  lcd.home();
  lcd.print("# offline mode #");
}

void show_online(void)
{
  lcd.clear();
  lcd.home();
  lcd.print("# online mode #");
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
