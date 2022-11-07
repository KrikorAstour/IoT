import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

import ssl
import time
import smtplib
from email.message import EmailMessage
import os
import email
import imaplib
from email.header import decode_header
import webbrowser
# import easyimap as imap
from flask import Flask, render_template
app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led = 21
ledStatus = 0
email_sender = 'turcanmadalina10@gmail.com'
email_password = 'mrnnlubhiibuhasp'
email_receiver = 'astour.krikor@gmail.com'
n_email_to_send = 1
display_temperature_message=True
imap_url = 'imap.gmail.com'

GPIO.setup(led, GPIO.OUT)

def sendEmail(payload):
    subject = "Photoresistor"
    body = "Light Intensity is "+ payload +". LED is On."
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

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    client.subscribe("/esp8266/data")

def on_message(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '" + message.topic)
    if(int(str(message.payload))){
        GPIO.output(led, GPIO.HIGH)
        sendEmail(str(message.payload))
    }
    else
        GPIO.output(led, GPIO.LOW)
    

def main():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    print("the main is running")
    mqtt_client.connect('localhost', 1883, 60) 
    # Connect to the MQTT server and process messages in a background thread. 
    mqtt_client.loop_start() 

if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()