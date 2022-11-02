from flask import Flask, request, jsonify
from flask_cors import CORS
from pymcprotocol import Type1E

app = Flask(__name__)
CORS(app)

pymc1e = Type1E()
    # pymc1e.connect('192.168.110.24', 1025)


sensors = {
    "M1": False,
    "M2": False,
    "M3": False,
    "M4": False
}
plc = True

@app.route('/api/update-buttons', methods=['POST'])
def update_buttons():

    pressed = request.json['pressed']
    state = request.json['state']

    return jsonify({pressed: state})


@app.route('/api/update-sensors', methods=['POST'])
def update_sensors():
    sensor = request.json['sensor']
    sensors[sensor] = not sensors[sensor]

    return jsonify(sensors)

@app.route('/api/update-plc', methods=['POST'])
def update_plc():
    plc = request.json['plc']

    return jsonify(plc)