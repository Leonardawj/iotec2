**ST0324 Internet of Things CA2 Step-by-step Tutorial**

##### SCHOOL OF DIGITAL MEDIA AND INFOCOMM TECHNOLOGY (DMIT)

# IOT CA2 Garbage Monitoring System

# Step-by-step Tutorial

ST 0324 Internet of Things (IOT)


## Table of Contents


- Section 1 Overview of Project
- Section 2 Hardware requirements
- Section 3 Hardware setup
- Section 4 Software requirements
- Section 5 Mosquitto(Master Device)
- Section 6 MQTT(Master Device)
- Section 7 Index.html
- Section 8 Slave 1
- Section 9 Slave 2
- Section 10 Database requirements
- Section 11 References


## Section 1 Overview of Garbage Monitoring System

### A. What is it about?

Our project is IOT Garbage Monitoring system is a very innovative system which will help to keep the cities clean. This system monitors the garbage bins and informs about the level of garbage collected in the garbage bins via a web page. For this the system uses ultrasonic sensors placed over the bins to detect the garbage level and compare it with the garbage bins depth. 100 means it is empty and 0 mean it is full.

### B. How the final RPI set-up looks like

```
Final Set-up
```

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image1.png "Optional title")

```
Overview of Garbage Monitor System internally
```

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image3.png "Optional title")

### C. How the web application looks like

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image2.png "Optional title")




## Section 2 Hardware requirements

### A. Hardware checklist

- 3 Raspberry Model B
- 2 Ultrasonic sensor
- 2 LCD Moniter
- 12 Female to male connector

## Section 3 Hardware setup

In this section, we will connect all the necessary components described in Section 2.

### Fritzing Diagram
```
Master Device
```
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image4.png "Optional title")

```
Slave 1
```
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image5.png "Optional title")

```
Slave 2
```
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image6.png "Optional title")


## Section 4 Software requirements

#### Software
- AWS
- Phpmyadmin

## Section 5 Mosquitto (Master Device)

#### Open First Terminal Windows

a) In the First Terminal window, make sure the Mosquitto broker is running

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image7.png "Optional title")

b) You should see another message in the first terminal window saying another client is connected.

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image8.png "Optional title")

c) You should also see this message in the subscriber terminal:

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image9.png "Optional title")

d) Troubleshoot
If u encountered error port in used.Use the following code to stop the mosquitto and then relaunch

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image10.png "Optional title")


## Section 6 MQTT (Master Device)

We code our MQTT_Subscriber file to communicate with broke slave devices, and interact with
our database.

#### Source code
```
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
        a = int((100 * int(sensor1))/25)
        if a > 100:
            a = 100
        b = int((100 * int(sensor2))/25)
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


if _name_ == "_main_":
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
```

#### Open Second Terminal Windows

In the Second Terminal window, make sure the MQTT is running
Once u have seen this result, this show that ur master device have suddenly connected to both of the slave device.

```
Sudo python mqtt_subscriber.py
```

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image11.png)

You should see another message in the first terminal window saying another client is connected and you should also see this message in the subscriber terminal:

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image12.png)


## Section 7 Index.html

#### Source Code

Now we will design our web interface to display the historical values and both real time
garbage bin

##### Source Code
```
<?php
	$servername = "localhost";
	$username = "root";
	$password = "dmitiot";
	$dbname = "iotgarbagemonitoring";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ($conn->connect_error) {
		die("Connection failed: " . $conn->connect_error);
	} 

	$sql = "SELECT *from sensor_data ORDER BY id DESC LIMIT 1";
	$result = $conn->query($sql);

	if ($result->num_rows == 1)
	{
		$row = $result->fetch_assoc();
		$sensor1 = $row["sensor1"];
		$sensor2 = $row["sensor2"];
	}
	else 
	{
		echo "0 results";
	}
	
	$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
	<head>
		<title>IOT Garbage Monitoring system</title>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="stylesheet" href="bootstrap.min.css">
		<script src="bootstrap.min.js"></script>
		<link rel="stylesheet" href="styles.css">
                          <meta http-equiv="refresh" content="5">
	</head>
	<body>
		<div class="jumbotron text-center">
		  <h1>IOT Garbage Monitoring system</h1>
		</div>
		<div class="container">
			<table class="table">
				<tr>
					<th class="jumbotron text-center">Container1</th>
					<th class="jumbotron text-center">Container2</th>
				</tr>
				<tr>
					<th>
						<div class="center">
							<div class="progress progress-bar-vertical">
								<div class="progress-bar" role="progressbar" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" <?php echo "style=\"height: ".$sensor1."%;\""; ?> > </div>
							</div>
						</div> 
						<div> <?php echo "Sensor1 : ". $sensor1; ?> </div>
					</th>
					<th>
						<div class="center">
							<div class="progress progress-bar-vertical">
								<div class="progress-bar" role="progressbar" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" <?php echo "style=\"height: ".$sensor2."%;\""; ?> > </div>  
							</div>
						</div>
						<div> <?php echo "Sensor2 : ". $sensor2; ?> </div>
					</th>
				</tr>
			</table>
			<br> <br> <br>
			<div class="jumbotron text-center">
				<h1>Data Log</h1>
			</div>
			<?php
				$conn = new mysqli($servername, $username, $password, $dbname);
				if ($conn->connect_error) {
					die("Connection failed: " . $conn->connect_error);
				} 
				$sql  = 'SELECT * FROM `sensor_data` WHERE 1';
				$result = $conn->query($sql);
				if ($result->num_rows > 0) 
				{
					echo "<table class=\"table\">"; 
					//echo "<tr><td>NO of Data : " . $result->num_rows . "</td></tr>";
					echo "<tr><td>ID</td><td>Sensor1</td><td>Sensor2</td><td>Date Time</td></tr>";
								
					while($row = $result->fetch_array(MYSQLI_ASSOC))
					{
						echo "<tr><td>" . $row['id'] . "</td><td>" . $row['sensor1'] . "</td><td>" . $row['sensor2'] . "</td><td>" . $row['date'] . "</td></tr>";
					}
					echo "</table>";
					$result->close();
				}
			?>
		</div>
	</body>
</html>
```
This is our index.html for our website as shown on section. It is a simple interface which consistent a real time and historical dataset.Our data is obtain every 10 sec.

## Section 8 Slave 1

The following codes are needed for the application to work. As there are 2 Garbage Bin, all the garbage bin have the same python code except that the string is a little different as 2 lots cannot have the same name. These files are provided in the ZIP folder but not the tutorial.

### A. Source Code (slave1.py)
```
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import time

broker_address="192.168.1.238"

# set GPIO Pins
GPIO_TRIGGER = 22	
GPIO_ECHO = 23


def ini_sensor():
    GPIO.cleanup()
    # GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)

    # set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = StopTime = time.time()
    #StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def main():
    ini_sensor()
    client = mqtt.Client("P1") 	#create new instance
    client.connect(broker_address) 	#connect to broker

    while True:
        dist = distance()
	dist = int(dist)
        print("Measured Distance="+str(dist))
	client.publish("channel1",dist)	#publish
	sleep(1)


if __name__ == "__main__":
    main()
```
### B. Open Terminal Window
In the Terminal window, make sure the code is running 
```
sudo python slave1.py
```
You should see the distance being measured in the following terminal

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image13.png)

This show that our ultrasonic sensor is reading is measuring the distance of our rubbish bin fromt the top to bot.


## Section 9 Slave 2 (slave2.py)

### A. Source Code 
```
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import time

broker_address="192.168.1.238"

# set GPIO Pins
GPIO_TRIGGER = 22	
GPIO_ECHO = 23


def ini_sensor():
    GPIO.cleanup()
    # GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)

    # set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = StopTime = time.time()
    #StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def main():
    ini_sensor()
    client = mqtt.Client("P1") 	#create new instance
    client.connect(broker_address) 	#connect to broker

    while True:
        dist = distance()
	dist = int(dist)
        print("Measured Distance="+str(dist))
	client.publish("channel1",dist)	#publish	sleep(1)


if __name__ == "__main__":
    main()
```

### B. Open Terminal Windows
In the Terminal window, make sure the code is running
```
sudo python slave2.py
```
You should see the distance being measured in the following terminal

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image14.png)

This show that our ultrasonic sensor is reading is measuring the distance of our rubbish bin fromt the top to bot.

## Section 10 Database requirements

#### Database set up
A) Set up a new AWSEducate account by accessing the website https://aws.amazon.com/education/awseducate/apply/
Select "Students" option

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image15.png)

B) Select Role as "Student"

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image16.png)

C) On the sign up form, ensure the following settings are specified, and fill in the rest of the form as appropriate and then click “Next” button.

D) Institution name is “Singapore Polytechnic School of EEE”
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image17.png)

Email is your SP ichat email address
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image18.png)

Click here to select an AWS Educate Starter” account is selected
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image19.png)

E) Follow the instructions to verify your account by providing a verification code that is sent to your ichat email account.

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image20.png)

F) Once your AWS account is ready for use, you will receive an email similar to this one

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image21.png)

### Sign in to AWS IOT Console
After you have received the email confirmation from AWS, you are now ready to log into the AWS IoT console to start the lab.

A) Log in your AWS Educate account using your ichat email address
https://www.awseducate.com/signin/SiteLogin

B) Click “AWS Account” You should be brought to a screen similar to this. Click AWS Console button.

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image36.png)

After a while, you will be brought in the AWS Management Console.

![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image23.png)

### EC2

A) Set up EC2
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image24.png)
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image25.png)
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image26.png)
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image27.png)
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image28.png)
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image29.png)
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image30.png)
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image31.png)

### Database Access
After you are done setting up, this is what you will see as the following

A) Instance Console
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image32.png)
```
Url for webpage : http://ec2-3-87-62-43.compute-1.amazonaws.com/iotgarbagemonitoring/
url for database : http://ec2-3-87-62-43.compute-1.amazonaws.com/phpmyadmin/
```
After you have log in to the database, create a database and name it as iotgarbagemonitoring
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image33.png)

Create a table called sensor_data in the database u have just created
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image34.png)

SQL structure for the table
![Alt text](https://github.com/Leonardawj/iotec2/blob/master/README%20images/Image35.png)


## Section 11 References

- AY1910s1 ST0324 IoT Practical 10
- AY1910s1 ST0324 IoT Practical 11


```
-- End of CA2 Step-by-step tutorial --
```
