import Adafruit_DHT
import time
import ssl
import time
import smtplib
from email.message import EmailMessage
import os
import email
import imaplib
from email.header import decode_header
import webbrowser

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
 
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 18
MOTOR_PIN1 = 22 # Enable Pin
MOTOR_PIN2 = 27 # Input Pin
MOTOR_PIN3 = 17 # Input Pin

GPIO.setup(MOTOR_PIN1,GPIO.OUT)
GPIO.setup(MOTOR_PIN2,GPIO.OUT)
GPIO.setup(MOTOR_PIN3,GPIO.OUT)

# Function to turn on the motor
def turnMotor():
    GPIO.output(MOTOR_PIN1,GPIO.HIGH)
    GPIO.output(MOTOR_PIN2,GPIO.LOW)
    GPIO.output(MOTOR_PIN3,GPIO.HIGH)

#     check temp
#     if higher than 24 send email
#     send email
n_email_to_send = 5
email_sender = 'turcanmadalina10@gmail.com'
email_password = 'mrnnlubhiibuhasp'
email_receiver = 'turcanmadalina10@gmail.com'
for i in range (n_email_to_send):
    subject = "Temperature is over 24" + str(i + 1)
    body = "The temperature is over 24. Would you like to turn on the fan? If so, reply Yes "
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
#     receive email
imap_url = 'imap.gmail.com'
imap = imaplib.IMAP4_SSL(imap_url)
imap.login(email_receiver, email_password)
status, messages = imap.select("INBOX
n_email_to_receive = 5
messages = int(messages[0])

#Iterate to display email
n = 0
for i in range(messages, messages-n_email_to_receive, -1):
    n = n + 1
    print("EMAIL:", n)
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # extract content type of email
            content_type = msg.get_content_type()
            # get the email body
            body = msg.get_payload(decode=True).decode()
            if content_type == "text/plain":
                if body == 'Yes'
                    # if yes
                    turnMotor()
imap.close()
imap.logout()



while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))

#     else:
#         print("Sensor failure. Check wiring.");
    time.sleep(3);
