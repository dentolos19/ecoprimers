import os

import stripe
from flask import Flask

initialized: bool = False


def init(app: Flask):
    global initialized

    if initialized:
        return

    app.config["STRIPE_SECRET_KEY"] = os.environ.get("STRIPE_SECRET_KEY")
    app.config["STRIPE_PUBLIC_KEY"] = os.environ.get("STRIPE_PUBLIC_KEY")

    stripe.api_key = app.config["STRIPE_SECRET_KEY"]

    initialized = True