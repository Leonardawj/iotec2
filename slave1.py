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
