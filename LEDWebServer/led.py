import RPi.GPIO as GPIO
from flask import Flask, render_template
app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led = 25
ledStatus = 0

GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

@app.route("/")
def index():
    ledStatus = GPIO.input(led)
    data = {
        'led' : ledStatus
    }
    return render_template('index.html', **data)

@app.route("/<action>")
def action(action):
    
    if action == "on":
        GPIO.output(led, GPIO.HIGH)
    if action == "off":
        GPIO.output(led, GPIO.LOW)
        
    ledStatus = GPIO.input(led)
    
    data = {
        'led' : ledStatus
    }
    return render_template('index.html', **data)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
