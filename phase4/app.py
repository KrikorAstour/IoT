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

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
MOTOR_PIN1 = 22 # Enable Pin
MOTOR_PIN2 = 27 # Input Pin
MOTOR_PIN3 = 17 # Input Pin

GPIO.setup(MOTOR_PIN1,GPIO.OUT)
GPIO.setup(MOTOR_PIN2,GPIO.OUT)
GPIO.setup(MOTOR_PIN3,GPIO.OUT)

led = 21
SH = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"
app = dash.Dash(external_stylesheets=[SH])
userInfo = "gggg"
emails_temp_sent = 0
krikorTag = "73 9c be 0d"
sarahTag = "e3 24 5d 0d"
tagNum = ""
temp = ""
hum = ""
ent = "blahhh"
email_sender = 'turcanmadalina10@gmail.com'
email_password = 'mrnnlubhiibuhasp'
email_receiver = 'astour.krikor@gmail.com'
n_email_to_send = 1
n_email_to_receive = 1
display_temperature_message=True
imap_url = 'imap.gmail.com'

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


def turnLight():
    GPIO.output(led,GPIO.HIGH)
    
def turnFan():
    print("fanON")
    GPIO.output(MOTOR_PIN1,GPIO.HIGH)
    GPIO.output(MOTOR_PIN2,GPIO.LOW)
    GPIO.output(MOTOR_PIN3,GPIO.HIGH)

def getUsers(ent):
    if ent == "Krikor":
        tag_num = krikorTag
    if ent == "Sarah":
        tag_num = sarahTag
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
    else:
        user = "Krikor"
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
                               className="ms-3",
                               children=[
                                   html.H5(children=[], id="output_username", className="mb-0")],),
                            html.Div(
                                className="navbar-nav w-100",
                                children=[
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
                                                                                children=[html.H6(children=[], id="output_rfid")]),
                                                                            
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
                                    ),
                                ],
                            ),
                            html.Div(
                                className="col-sm-6 col-xl-3",
                                children=[
                                    html.Div(
                                        className="bg-secondary rounded d-flex align-items-center justify-content-between p-4",
                                        children=[
                                            html.Div(
                                                className="ms-3",
                                                children=[
                                                    html.P("Other Devices", className="mb-2"),
                                                    html.H6("Number here", className="mb-0")],)
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
      Output(component_id="output_rfid", component_property="children"),
      Output(component_id="output_gauge", component_property="value"),
     Output(component_id="output_resistor", component_property="children"),
     Output(component_id="output_light_img", component_property="src")],
     [Input(component_id="my_interval", component_property="n_intervals")]
)
def update_stuff(n_intervals):
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
         emails_temp_sent = 0
    else:
        print("ss")
        ent = getRfid()
        if ent != None:
            myList = getUsers(ent)
            user, favetemp, faveHumid, faveLight = displayInfo(myList)
            print("last ent"+ent)
        else:
            user, favetemp, faveHumid, faveLight = "","","",""
        out_res = pResistor
        print(out_res)
        light_intensity = int(out_res)
        if faveLight != None:
            if light_intensity < int(faveLight):
                 turnLight()
                 out_img = app.get_asset_url('lighton.jpg')
                 time.sleep(3)
            else:
                GPIO.output(21,GPIO.LOW)
                out_img = app.get_asset_url('lightoff.jpg')
        curtemp = temp
        output_therm = int(temp)
        curhum = hum
        output_gau = int(hum)
        
        print(output_therm > favetemp)
        print(emails_temp_sent <= 0)
        if output_therm > favetemp:
            if emails_temp_sent <= 0:
                print("we should be good")
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
    return user, favetemp, faveHumid, faveLight, curtemp, output_therm, curhum, ent, output_gau, out_res, out_img

if __name__ == '__main__':
    app.run_server(debug=True, port=8053)