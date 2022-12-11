import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import dash_daq as daq
import paho.mqtt.client as mqtt
import sqlite3
from mqtt import *
from resistor import *
import RPi.GPIO as GPIO
import time
import bluetooth
# from devicess import *

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
MOTOR_PIN1 = 22 # Enable Pin
MOTOR_PIN2 = 27 # Input Pin
MOTOR_PIN3 = 17 # Input Pin

GPIO.setup(MOTOR_PIN1,GPIO.OUT)
GPIO.setup(MOTOR_PIN2,GPIO.OUT)
GPIO.setup(MOTOR_PIN3,GPIO.OUT)

led = 21
scanned = False
SH = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"
app = dash.Dash(external_stylesheets=[SH])
userInfo = "gggg"
emailCount = 0
krikorTag = "73 9c be 0d"
sarahTag = "e3 24 5d 0d"
madalinaTag = "13 05 5e 0d"
fan_img =  app.get_asset_url('fan-off.png')
tagNum = ""
temp = ""
hum = ""
ent = "blahhh"
email_sender = ''
email_password = ''
email_receiver = 'astour.krikor@gmail.com'
n_email_to_send = 1
n_email_to_receive = 1
display_temperature_message=True
imap_url = 'imap.gmail.com'
noAnswer = True

def bluetoothScan():
    global bluetooth, scanned
    print("Scanning for bluetooth devices:")
    devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True)
    number_of_devices = len(devices)
    # print(number_of_devices,"devices found")
    scanned = True
    
    return number_of_devices

def sendEmail(subject_param, body_param):
    subject = subject_param
    body = body_param
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
                            return body                               
                else:
                    # Extract content type of email
                    content_type = msg.get_content_type()
                    # Get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # Return informations
                        return body

                print("="*100)
    # Close the connection and logout
    imap.close()
    imap.logout()


def turnLight():
    GPIO.output(led,GPIO.HIGH)
    
def turnFan():
    global emailCount
    print("fanON")
    GPIO.output(MOTOR_PIN1,GPIO.HIGH)
    GPIO.output(MOTOR_PIN2,GPIO.LOW)
    GPIO.output(MOTOR_PIN3,GPIO.HIGH)
    emailCount = 0

def getUsers(ent):
    if ent == "Krikor":
        tag_num = krikorTag
    if ent == "Sarah":
        tag_num = sarahTag
    if ent == "Madalina":
        tag_num = madalinaTag
    con = sqlite3.connect("people.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM users WHERE tag_num = :tag_num", {'tag_num': tag_num})
    #con.close()
    return res.fetchall()
    
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    client.subscribe("/esp8266/data")
    client.subscribe("/esp8266/resistor")
    client.subscribe("/esp8266/humidity")
    client.subscribe("/esp8266/temperature")
    
def on_message(client, userdata, message):
    global pResistor, led2status, tagNum, hum, temp
#     print(message.payload)
    if message.topic == "/esp8266/data":
        tagNum = str(message.payload)[3:14]
    if message.topic == "/esp8266/resistor":    
        pResistor = str(message.payload)[2:5]
    if message.topic == "/esp8266/humidity":    
        hum = str(message.payload)[3:5]
    if message.topic == "/esp8266/temperature":    
        temp = str(message.payload)[3:5]
#     print("temp",temp)
#     print("hum",hum)
   
def displayInfo(mylist):
    if mylist[0][0] == sarahTag:
        user = "Sarah"
    elif mylist[0][0] == krikorTag:
        user = "Krikor"
    else:
        user = "Madalina"
    temp = mylist[0][1]
    hum = mylist[0][2]
    light = mylist[0][3]
    return user, temp, hum, light
    

def getRfid():
#     mqtt_client = mqtt.Client()
#     mqtt_client.on_connect = on_connect
#     mqtt_client.on_message = on_message
#     mqtt_client.connect('localhost', 1883, 60)
#     mqtt_client.loop_start()
    entered = ""
    if krikorTag == tagNum:
        entered = "Krikor"
        return entered
    if sarahTag == tagNum:
        entered = "Sarah"
        return entered
    if madalinaTag == tagNum:
        entered = "Madalina"
        return entered
    else:
        return None
    #print("entered in get"+entered)
#     sendEmail(userInfo)
    


#import and clean data lateron

#app layout
app.layout = html.Div([
        dcc.Interval(id="my_interval", interval=1*5000, n_intervals=0),
        html.Div(
        className="container-fluid position-relative d-flex p-0",
        children=[
            dcc.Dropdown(id="input_select", options=[{"label": "this is input", "value": 2}]),
            html.Div(
                className="sidebar pe-4 pb-3",
                children=[
                   html.H3("IoT Dashboard", className="text-primary"),
                    html.Div(
                        className="d-flex align-items-center ms-4 mb-4",
                        children=[
                           
                            html.Div(
                                className="navbar-nav w-100",
                                children=[
                                    html.H5(children=[], id="output_username"),
                                    html.H6(children=[], id="output_favTemp"),
                                    html.H6(children=[], id="output_favHumid"),
                                    html.H6(children=[], id="output_faveLight")
                                    ]),
                    ]),
            ]),
            html.Div(
                className="content",
                children=[
                    html.Div(
                        className="container-fluid pt-4 px-4",
                        children=[
                            html.Div(
                                className="row g-4",
                                children=[
                                    html.Div(
                                        className="col-sm-12 col-xl-6",
                                        children=[
                                            html.Div(
                                                className="bg-secondary text-center rounded p-4",
                                                children=[
                                                    html.Div(
                                                        className="d-flex align-items-center justify-content-between mb-4",
                                                        children=[
                                                            html.H5("Thermometer System", className="mb-0"),
                                                            html.Br(),
                                                            html.Div(
                                                                className="container",
                                                                children=[
                                                                    html.Div(
                                                                        className="row",
                                                                        children=[
                                                                            html.Div(
                                                                                className="col",
                                                                                children=[html.Br(), html.H6(children=[], id="output_currentTemp"), daq.Thermometer(id="output_therm", value=0 , min=0, max=30, height=150, width=5)]),
                                                                            html.Div(
                                                                                className="col",
                                                                                children=[html.Br(),html.H6(children=[], id="output_currentHumid"), daq.Gauge(id="output_gauge", value= 0, min=0, max=100, size=150)]),
                                                                            html.Div(
                                                                                className="col",
                                                                                children=[html.Img(id = "output_fan_img",src="", style={'height':'30%', 'width':'100%'})]),
                                                                            
                                                                        ]),
                                                                ],),
                                                            ],),
                                                    ],
                                            ),
                                            
                                        ],
                                    ),
                                ],
                            ),    
                        ],
                    ),
                    html.Div(
                        className="container-fluid pt-4 px-4",
                        children=[
                            html.Div(
                                className="row g-4",
                                children=[
                                    html.Div(
                                        className="col-sm-6 col-xl-3",
                                        children=[
                                            html.Div(
                                                className="bg-secondary rounded d-flex align-items-center justify-content-between p-4",
                                                children=[
                                                    html.Div(
                                                        className="ms-3",
                                                        children=[
                                                            html.P("Light", className="mb-2"),
                                                            html.H6(children=[], id="output_resistor"),
                                                            html.Img(id = "output_light_img",src="", style={'height':'35%', 'width':'35%'})]
                                                            )
                                                    ],
                                            ), 
                                        ],
                                    ),html.Div(
                                className="col-sm-6 col-xl-3",
                                children=[
                                    html.Div(
                                        className="bg-secondary rounded d-flex align-items-center justify-content-between p-4",
                                        children=[
                                            html.Div(
                                                className="ms-3",
                                                children=[
                                                    html.P("Bluetooth Devices Found: 2", className="mb-2"),
                                                    html.H6(children=[], id="output_blue")],),
                                                    html.Br(),
                                                    html.Br(),
                                            ],
                                    ),
                                ],
                            ),
                                ],
                            ),
                            
                        ],
                    ),
            ]),
        ])
    ])
    
@app.callback(
     [Output(component_id="output_username", component_property="children"),
      Output(component_id="output_favTemp", component_property="children"),
      Output(component_id="output_favHumid", component_property="children"),
      Output(component_id="output_faveLight", component_property="children"),
      Output(component_id="output_currentTemp", component_property="children"),
      Output(component_id="output_therm", component_property="value"),
      Output(component_id="output_currentHumid", component_property="children"),
      Output(component_id="output_fan_img", component_property="src"),
      Output(component_id="output_gauge", component_property="value"),
      Output(component_id="output_resistor", component_property="children"),
      Output(component_id="output_light_img", component_property="src")],
    #   Output(component_id="output_fan_img", component_property="src")],
    #   Output(component_id="output_blue", component_property="src")],
     [Input(component_id="my_interval", component_property="n_intervals")]
)
def update_stuff(n_intervals):
    global emailCount, noAnswer, fan_img
#   will retrieve from db
    #temps = [22,25,14,0,26,27]
#     if n_intervals == 0:
#         mqtt_client = mqtt.Client()
#         mqtt_client.on_connect = on_connect
#         mqtt_client.on_message = on_message
#         mqtt_client.connect('localhost', 1883, 60)
#         mqtt_client.loop_start()
#         
#         #raise PreventUpdate
#     else:
#       get data here
#         ent = getRfid()
        
        #print("entered: "+entered)
        #curhum = getTemp()
        #output_therm = curtemp
        #output_gau = curhum
    if n_intervals == 0:
         mqtt_client = mqtt.Client()
         mqtt_client.on_connect = on_connect
         mqtt_client.on_message = on_message
         mqtt_client.connect('localhost', 1883, 60)
         mqtt_client.loop_start()
         
    else:
        ent = getRfid()
        if ent != None:
            myList = getUsers(ent)
            user, favetemp, faveHumid, faveLight = displayInfo(myList)
            print("Last Entered: "+ent)
        else:
            user, favetemp, faveHumid, faveLight = "Username: ","Temperature: ","Humidity: ","Light: "
        out_res = pResistor
        print(out_res)
        light_intensity = int(out_res)
        if faveLight != None:
            if light_intensity < int(faveLight):
                 turnLight()
                 out_img = app.get_asset_url('bulb-on.png')
                 time.sleep(3)
            else:
                GPIO.output(21,GPIO.LOW)
                out_img = app.get_asset_url('bulb-off.png')
        curtemp = temp
        output_therm = int(temp)
        curhum = hum
        output_gau = int(hum)
        
        
        print("EmailCount before: ", emailCount)
        if output_therm > favetemp and emailCount <=0:
            sendEmail("Smart Fan","Would You like to turn the fan?")
            emailCount = 1
            time.sleep(20)
            while noAnswer:
                print("in While")
                body = receiveEmail(email_sender, email_password, imap_url, n_email_to_receive)
                
#                 print("after sleep")
                # print("body", body)
                if body.upper().count("YES"):
                    fan_img =  app.get_asset_url('fan-on.png')
                    turnFan()
                    noAnswer = False
                elif body.upper().count("NO"):
                    print("answer no")
                    fan_img =  app.get_asset_url('fan-off.png')
                    noAnswer = False
                    emailCount = 0
                else:
                    print("nothing haened at all")
                    noAnswer = True
                    
        
        print("EmailCount After: ", emailCount)
        if scanned == False:
            print("Bluetooth Devices: ", bluetoothScan())
        # blue_num = scanBlue()
#         print(emails_temp_sent <= 0)
#         if output_therm > favetemp:
#             if emails_temp_sent <= 0:
#                 print("we should be good")
#         if output_therm > favetemp and emails_temp_sent == 0:
#             print("in if condition")
#             emails_temp_sent+1
#             sendEmail("Temperature is over your threshold", "The temperature is over your threshold, would you like to turn on the fan? If so, reply Yes. bitch")
#             if yes
#                 turnFan()
        
#         print("list:", getUsers(ent))
        
    #     user = myList[0][0]
#         print("user", myList[0][0])
#     favetemp = myList[0][1]
#     faveHumid = myList[0][2]
#     faveLight = myList[0][3]
    
#curtemp = 22
    #curhum = 30
    
    #returning otuputs
      
    return "Username:\t"+user, "User Temp:\t"+str(favetemp), "User Humidity:\t"+str(faveHumid), "User Light:\t"+str(faveLight), curtemp, output_therm, curhum, fan_img, output_gau, out_res, out_img

if __name__ == '__main__':
    app.run_server(debug=True, port=8055)
