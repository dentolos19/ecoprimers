from flask import Flask

import ai
import database

app = Flask(__name__)
app_debug = bool(app.config["DEBUG"])
app.config['SECRET_KEY'] = 'hello_world'
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51QTbV1RxRE93gjFvwRYd8vXJs3I2EYbvQL9HEsHi5jO15gcl5yxFSEX0jCbqbNOFTVB1UbJ0fls6IBiAlb7SxqKr00nkH3rTtA'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51QTbV1RxRE93gjFvaH6iZkVPr6mIPAMR7e1qMU27ENHGy3xzYV2GlHTBQhzfkkYqlsMcQ4dsLyXgk2bUJpWSnDSk00FUt2y6vq'

# Initialize internal systems
ai.init()
database.init(local=app_debug)

# Import routes into the main module
from api import *
from routes import *

if __name__ == "__main__":
    app.run()