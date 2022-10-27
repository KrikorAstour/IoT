import RPi.GPIO as GPIO
import Adafruit_DHT
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

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 18
led = 25
ledStatus = 0
email_sender = 'turcanmadalina10@gmail.com'
email_password = 'mrnnlubhiibuhasp'
email_receiver = 'astour.krikor@gmail.com'
n_email_to_send = 1
n_email_to_receive = 1
display_temperature_message =  True
imap_url = 'imap.gmail.com'
isMotorOn = 0

GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

MOTOR_PIN1 = 22 # Enable Pin
MOTOR_PIN2 = 27 # Input Pin
MOTOR_PIN3 = 17 # Input Pin

GPIO.setup(MOTOR_PIN1,GPIO.OUT)
GPIO.setup(MOTOR_PIN2,GPIO.OUT)
GPIO.setup(MOTOR_PIN3,GPIO.OUT)

# reading temperature
def getTemp():
    while True:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            return temperature

# Function to turn on the motor
def turnMotor():
    GPIO.output(MOTOR_PIN1,GPIO.HIGH)
    GPIO.output(MOTOR_PIN2,GPIO.LOW)
    GPIO.output(MOTOR_PIN3,GPIO.HIGH)

def sendEmail(temperature):
    subject = "Temperature is over 24"
    body = "The temperature is "+str(temperature)+". Would you like to turn on the fan? If so, reply Yes "
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

def receiveEmail(email_receiver, email_password, imap_url, n_email_to_receive):
    # Connection with GMAIL using SSL
    imap = imaplib.IMAP4_SSL(imap_url)
    imap.login(email_receiver, email_password)
    status, messages = imap.select("INBOX")
    # Total number of emails
    messages = int(messages[0])
    # Iterate to display email
    n = 0
    for i in range(messages, messages - n_email_to_receive, -1):
        n = n + 1
        # Fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # Parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # Decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # If it is a bytes, decode to str
                    try: subject = subject.decode(encoding)
                    except: pass
                # Decode email sender
                sender, encoding = decode_header(msg.get("From"))[0]
                if isinstance(sender, bytes):
                    try: sender = sender.decode(encoding)
                    except: pass
                # If the email message is multipart
                if msg.is_multipart():
                    # Iterate over email parts\saved\
                    for part in msg.walk():
                        # Extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # Get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # Return informations
                            return subject, sender, body                               
                else:
                    # Extract content type of email
                    content_type = msg.get_content_type()
                    # Get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # Return informations
                        return subject, sender, body

                print("="*100)
    # Close the connection and logout
    imap.close()
    imap.logout()

def turnMotorBasedOnAnswer(): 
    time.sleep(5)
    subject, sender, body = receiveEmail(email_receiver, email_password, imap_url, n_email_to_receive)
#     if body.count("The temperature is") and display_temperature_message == True:
#         print("\nSender:", sender)
#         print("Subject:", subject)
#         print("Message:", body)
#         display_temperature_message = False
    if body.upper().count("YES"): 
        print("Fan is activated")
        isMotorOn = 1
        turnMotor()
#         sendEmail(email_sender, email_receiver, email_password, subject, "Fan is activated")
#         quit()
    elif body.upper().count("NO"):
        print("Fan is not activated") 
#         sendEmail(email_sender, email_receiver, email_password, subject, "Fan is not activated")
#         quit() 
    else: pass

@app.route("/")
def index():
    temp = getTemp()
    if temp > 24:
        sendEmail(temp)
        turnMotorBasedOnAnswer()
    data = {
        'dht11' : temp,
        'motor' : isMotorOn
    }
    ledStatus = GPIO.input(led)
    return render_template('index.html', **data)

# @app.route("/<action>")
# def action(action):
    
#     if action == "on":
#         GPIO.output(led, GPIO.HIGH)
#     if action == "off":
#         GPIO.output(led, GPIO.LOW)
        
#     ledStatus = GPIO.input(led)
    
#     data = {
#         'led' : ledStatus
#     }
#     return render_template('index.html', **data)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=59, debug=True)
