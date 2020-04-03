#!/usr/bin/env python

print("Main Start")
from modules import socketio, app, cbpi
from modules.core.hardware import SensorActive

try:
    port = int(cbpi.get_config_parameter('port', '5000'))
except ValueError:
    port = 5000

num_users = 0
#@socketio.on('connect')
def RestartSensors():
    global num_users
    num_users = num_users + 1
    if num_users == 1:
        cbpi.init_sensors()

#app.debug=True
print("Starting SocketIO socket")
socketio.run(app, host='192.168.0.30', port=port)