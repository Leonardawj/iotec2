import paho.mqtt.client as mqtt
import os
import threading
from time import sleep
import MySQLdb
import datetime
import smbus
import time

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1
 
MQTT_SERVER = "localhost"
MQTT_PATH1 = "channel1"
MQTT_PATH2 = "channel2"

sensor1 = 0
sensor2 = 0

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

  
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
    

# The callback for when the client receives a CONNACK response from the server.
def on_connect1(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH1)

# The callback for when the client receives a CONNACK response from the server.
def on_connect2(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH2)
 
# The callback for when a PUBLISH message is received from the server.
def on_message1(client, userdata, msg):
    global sensor1
    if msg.topic == 'channel1':
        sensor1 = msg.payload
        print("ch1:-"+sensor1)

def on_message2(client, userdata, msg):
    global sensor2
    if msg.topic == 'channel2':
        sensor2 = msg.payload
        print("ch2:-"+sensor2)

def client1_fxn(args):
    args.loop_forever()

def client2_fxn(args):
    args.loop_forever()

def main():
    global sensor1
    global sensor2
    print("Start")
    client1 = mqtt.Client()
    client1.on_connect = on_connect1
    client1.on_message = on_message1
 
    client2 = mqtt.Client()
    client2.on_connect = on_connect2
    client2.on_message = on_message2
    
    client1.connect(MQTT_SERVER, 1883, 60)
    client2.connect(MQTT_SERVER, 1883, 60)
   
    threading.Thread(target=client1_fxn, args=(client1,)).start()
    threading.Thread(target=client2_fxn, args=(client2,)).start()

    db = MySQLdb.connect(host="ec2-3-87-62-43.compute-1.amazonaws.com", user="root", passwd="password", db="iotgarbagemonitoring")
    cur=db.cursor()

    lcd_init()
   
    while 1:
        datetime1 = datetime.datetime.now()
        a = int((100 * int(sensor1))/10)
        if a > 100:
            a = 100
        b = int((100 * int(sensor2))/10)
        if b > 100:
            b = 100

        line1 = "Sensor 1 : " + str(a)
        line2 = "Sensor 2 : " + str(b)

        # Send some test
        lcd_string(line1,LCD_LINE_1)
        lcd_string(line2,LCD_LINE_2)
    
        try:
            cur.execute("""INSERT INTO `sensor_data`(`sensor1`, `sensor2`, `date`) VALUES (%s,%s,%s)""",(a,b,datetime1))
            db.commit()
            #print("DB Added")
        except:
            print("Db error")
            db.rollback()
        sleep(10)
            
    cur.close()
    db.close ()


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
