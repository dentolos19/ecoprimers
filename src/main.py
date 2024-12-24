from flask import Flask

import ai
import database

app = Flask(__name__)

# Initialize internal systems
ai.init()
database.init(local=False)

# Import routes into the main module
from api import *
from routes import *

if __name__ == "__main__":
    app.run()