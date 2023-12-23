from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'caught'

bcrypt = Bcrypt(app)  


from flask_app.controllers import users, sightings