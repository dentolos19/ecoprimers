import os

from flask import Flask
from flask_socketio import SocketIO

import ai
import database

app = Flask(__name__)
app_debug = bool(app.config["DEBUG"])
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["STRIPE_SECRET_KEY"] = os.environ.get("STRIPE_SECRET_KEY")
app.config["STRIPE_PUBLIC_KEY"] = os.environ.get("STRIPE_PUBLIC_KEY")

# Initialize internal systems
ai.init(app)
database.init(app, local=app_debug)

socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes into the main module
from api import *
from routes import *

if __name__ == "__main__":
    app.run()