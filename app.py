from flask import Flask, request, jsonify
from flask_cors import CORS
from pymcprotocol import Type1E

app = Flask(__name__)
CORS(app)

pymc1e = Type1E()
# pymc1e.connect('192.168.110.24', 1025)


sensors = {
    "M0": False,
    "M1": False,
    "M2": False,
    "M3": False
}

buttons = {
    "M4": False,
    "M5": False,
    "M6": False,
    "M7": False,
}

potentiometer = 0

@app.route('/')
def index():
    return "Test"

@app.route('/api/update-buttons', methods=['POST'])
def update_buttons():
    button = request.json['button']
    buttons[button] = not buttons[button]
    # pymc1e.randomwrite_bitunits(["M4"], [state])

    return jsonify(buttons[button])

@app.route('/api/update-potentiometer', methods=['POST'])
def update_potentiometer():
    global potentiometer
    temp = request.json['potentiometer']
    if potentiometer != temp:
        potentiometer = temp
        # pymc1e.randomwrite_bitunits(["M8"], [potentiometer])

    return jsonify(potentiometer)

@app.route('/api/update-sensors', methods=['POST'])
def update_sensors():
    sensor = request.json['sensor'].upper()
    sensors[sensor] = not sensors[sensor]
    # pymc1e.batchwrite_wordunits([sensor], sensors[sensor])

    return jsonify(sensors)

@app.route('/api/update-plc', methods=['POST'])
def update_plc():
    plc = request.json['plc']

    # if plc:
    #     pymc1e.remote_run()
    # else:
    #     pymc1e.remote_stop()

    return jsonify(plc)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True, threaded=False, ssl_context='adhoc')
