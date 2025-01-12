from flask import Flask

import os
import ai
import database

app = Flask(__name__)
# Configuration for the Flask app and database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to save uploaded images

app_debug = bool(app.config["DEBUG"])

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize internal systems
ai.init()
database.init(local=app_debug)

# Import routes into the main module
from api import *
from routes import *

if __name__ == "__main__":
    app.run()