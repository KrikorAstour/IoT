import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import dash_daq as daq
import paho.mqtt.client as mqtt
import sqlite3
from mqtt import *



SH = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"
app = dash.Dash(external_stylesheets=[SH])
userInfo = "gggg"
krikorTag = "73 9c be 0d"
sarahTag = "e3 24 5d 0d"
tagNum = ""
ent = "blahhh"

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
    
def on_message(client, userdata, message):
    global pResistor, led2status, tagNum
   
    tagNum = str(message.payload)[3:14]
    print(tagNum+" tag")
  
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
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect('localhost', 1883, 60)
    mqtt_client.loop_start()
    entered = ""
    if krikorTag == tagNum:
        entered = "Krikor"
    if sarahTag == tagNum:
        entered = "Sarah"
    print("ent "+entered)
    return entered
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
                                                                                children=[html.Br(), html.H6(children=[], id="output_currentTemp"), daq.Thermometer(id="output_therm", min=0, max=30, height=150, width=5)]),
                                                                            html.Div(
                                                                                className="col",
                                                                                children=[html.Br(),html.H6(children=[], id="output_currentHumid"), daq.Gauge(id="output_gauge", value= 20, min=0, max=100, size=150)]),
                                                                            html.Div(
                                                                                className="col",
                                                                                children=[html.H6(children=[], id="output_rfid")]),
                                                                            html.Div(
                                                                                className="col",
                                                                                children=[html.H6("Bluetooth devices: "+ getRfid())]),
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
                                                            html.H6("image be here", className="mb-0")],)
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
      Output(component_id="output_gauge", component_property="value")],
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
    ent = getRfid()
    myList = getUsers(ent)
    print("last ent"+ent)

    
    print("list:", getUsers(ent))
    user, favetemp, faveHumid, faveLight = displayInfo(myList)
#     user = myList[0][0]
    print("user", myList[0][0])
#     favetemp = myList[0][1]
#     faveHumid = myList[0][2]
#     faveLight = myList[0][3]
    curtemp = 22
    output_therm = 22
    curhum = 30
    output_gau = 30
#curtemp = 22
    #curhum = 30
    
    #returning otuputs
    return user, favetemp, faveHumid, faveLight, curtemp, output_therm, curhum, ent, output_gau

if __name__ == '__main__':
    app.run_server(debug=True, port=8053)