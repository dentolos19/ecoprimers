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


def pay(amount: float, success_url: str, cancel_url: str):
    return stripe.checkout.Session.create(
        payment_method_types=["card", "paynow"],
        line_items=[
            {
                "price_data": {
                    "currency": "sgd",
                    "product_data": {
                        "name": "Donation",
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
