#!/usr/bin/env python

from modules import socketio, app, cbpi

try:
  port = int(cbpi.get_config_parameter('port', '5000'))
except ValueError:
  port = 5000

app.debug=True
socketio.run(app, host='192.168.0.30', port=port)