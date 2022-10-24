# app/routes.py

from email.utils import formatdate
from app import app
from pymcprotocol import Type1E
import json

@app.route('/')
def index():
    return "Hi there!"

class Sensor:
    def __init__(self, sensor, active):
        self.sensor = sensor
        self.active = active

sensor1 = Sensor('M0', False)
sensor2 = Sensor('M1', False)
sensor3 = Sensor('M2', False)
sensor4 = Sensor('M3', False)


@app.route('/buttons-status/<data>', methods = ['POST'])
def buttonsStatus(data):
    # pymc1e = Type1E.connect('192.168.110.24', 1025)
    # pymc1e.randomwrite_bitsunits(['M0'], [1])
    formatData = json.loads(data)

    return str(formatData['state'])

@app.route('/sensors-state/<data>', methods = ['POST'])
def sensorsState(data):
    return data