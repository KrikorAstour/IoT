
import RPi.GPIO as GPIO
# import bluetooth

import ssl
import time
import smtplib
from email.message import EmailMessage
import os
import email
import imaplib
import paho.mqtt.client as mqtt
from email.header import decode_header
import webbrowser
# import easyimap as imap
# from flask import Flask, render_template
# app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led = 21
ledStatus = 0
pResistor = 0
led2status = 0
intValue = 0
krikorTag = "73 9c be 0d"
sarahTag = "e3 24 5d 0d"
madalinaTag = "dsw"
bluetooth = ""

tagNum = ""
# userInfo = ""
email_sender = 'turcanmadalina10@gmail.com'
email_password = 'mrnnlubhiibuhasp'
email_receiver = 'astour.krikor@gmail.com'
n_email_to_send = 1
display_temperature_message=True
imap_url = 'imap.gmail.com'

GPIO.setup(led, GPIO.OUT)

def sendEmail(payload):
    subject = "RFID"
    body = " "+ payload +" "
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    time.sleep(1)
    
def bluetoothScan():
    global bluetooth
    print("Scanning for bluetooth devices:")
    devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True)
    number_of_devices = len(devices)
    print(number_of_devices,"devices found")
    for addr, name, device_class in devices:
        bluetooth+=("\n")
        bluetooth+=("Device:")
        bluetooth+=("Device Name: %s" % (name))
        bluetooth+=("Device MAC Address: %s" % (addr))
        bluetooth+=("Device Class: %s" % (device_class))
        bluetooth+=("\n")
    return bluetooth

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    client.subscribe("/esp8266/data")
    
def getRfid():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect('localhost', 1883, 60) 
    # Connect to the MQTT server and process messages in a background thread. 
    mqtt_client.loop_start()
    if krikorTag == tagNum:
        print("in loop")
        return "Krikor Entered"
    if(sarahTag == tagNum):
        return "Sarah Entered"
    if(madalinaTag == tagNum):
        userInfo = "Madalina Entered"
    #print (krikorTag == tagNum)
    return "yo"
#     sendEmail(userInfo)
    
                
    

def on_message(client, userdata, message):
    global pResistor, led2status, tagNum
    print(str(message.payload))
   
    tagNum = str(message.payload)[3:14]
    print("get rfid"+getRfid())

    

def main():
#     mqtt_client = mqtt.Client()
#     mqtt_client.on_connect = on_connect
#     mqtt_client.on_message = on_message
#     mqtt_client.connect('localhost', 1883, 60) 
#     # Connect to the MQTT server and process messages in a background thread. 
#     mqtt_client.loop_start()
    getRfid()

# @app.route("/")
# def index():
#     mqtt_client = mqtt.Client()
#     mqtt_client.on_connect = on_connect
#     mqtt_client.on_message = on_message
#     mqtt_client.connect('localhost', 1883, 60) 
#     # Connect to the MQTT server and process messages in a background thread. 
#     mqtt_client.loop_start()
#     temp=0
#     isMotorOn = 0;
#     dht11 = 0;
#     
# #     if temp > 24:
# #     sendEmail(temp)
#     
# #     turnMotorBasedOnAnswer()
#     
#     print("ismotor = ", isMotorOn)
#     data = {
#         'dht11' : temp,
#         'motor' : isMotorOn,
#         'pResistor' : intValue,
#         'led2' : led2status
#     }
    
#     ledStatus = GPIO.input(led)
#     return render_template('index.html', **data)


if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=59, debug=True)
    main()
