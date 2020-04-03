print("Loading Basic Auth")
from modules import app, cbpi
try:
  from flask_basicauth import BasicAuth
except:
  import os
  os.system('pip install Flask-BasicAuth')
  from flask_basicauth import BasicAuth

basic_auth = BasicAuth(app)
def auth_password():
  password = cbpi.get_config_parameter('auth_password', None)
  if password is None:
    cbpi.add_config_parameter("auth_password", "password", "text", "HTTP Auth password")
    return "password"
  else:
    return password

print("Basic auth decorator")
@cbpi.initalizer(order=1)
def init_basic_auth(self):
  print("Basic auth function running")
  app.config['BASIC_AUTH_USERNAME'] = 'admin'
  app.config['BASIC_AUTH_PASSWORD'] = auth_password()
  app.config['BASIC_AUTH_FORCE'] = True
