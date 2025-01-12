import os

import stripe
from flask import Flask
from flask_socketio import SocketIO

import os
import ai
import database

app = Flask(__name__)
# Configuration for the Flask app and database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to save uploaded images

app_debug = bool(app.config["DEBUG"])
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["STRIPE_SECRET_KEY"] = os.environ.get("STRIPE_SECRET_KEY")
app.config["STRIPE_PUBLIC_KEY"] = os.environ.get("STRIPE_PUBLIC_KEY")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize internal systems
ai.init(app)
database.init(app, local=app_debug)

socketio = SocketIO(app, cors_allowed_origins="*")
stripe.api_key = app.config["STRIPE_SECRET_KEY"]

# Import routes into the main module
from api import *
from routes import *

if __name__ == "__main__":
    app.run()