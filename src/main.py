from flask import Flask

import ai
import database
from environment import SECRET_KEY, STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY

app = Flask(__name__)
app_debug = bool(app.config["DEBUG"])
app.config["SECRET_KEY"] = SECRET_KEY
app.config["STRIPE_PUBLIC_KEY"] = STRIPE_PUBLIC_KEY
app.config["STRIPE_SECRET_KEY"] = STRIPE_SECRET_KEY

# Initialize internal systems
ai.init()
database.init(local=app_debug)

# Import routes into the main module
from api import *
from routes import *

if __name__ == "__main__":
    app.run()