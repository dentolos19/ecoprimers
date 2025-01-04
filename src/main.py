from flask import Flask

import ai
import database

app = Flask(__name__)
app_debug = bool(app.config["DEBUG"])
app.config["SECRET_KEY"] = "hello_world"

# Initialize internal systems
ai.init()
database.init(local=app_debug)

# Import routes into the main module
from api import *
from routes import *

if __name__ == "__main__":
    app.run()