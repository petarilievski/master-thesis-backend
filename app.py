from flask import Flask, request, jsonify
from flask_cors import CORS
from pymcprotocol import Type1E
app = Flask(__name__)
CORS(app)

sensors = {
    "M1": False,
    "M2": False,
    "M3": False,
    "M4": False
}

@app.route('/api/update-buttons', methods=['POST'])
def update_buttons():
    pressed = request.json['pressed']
    state = request.json['state']

    return jsonify({pressed: state})


@app.route('/api/update-sensors', methods=['POST'])
def update_buttons():
    sensor = request.json['sensor']
    sensors[sensor] = not sensors[sensor]

    return jsonify({sensor})