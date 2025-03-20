import os
from typing import Any

from authlib.integrations.flask_client import OAuth
from flask import Flask

initialized: bool = False
auth: Any = None


def init(app: Flask):
    global initialized
    global auth

    # Skip if OAuth is already initialized
    if initialized:
        return

    app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET")
    app.config["GOOGLE_RECAPTCHA_SITE_KEY"] = os.environ.get("GOOGLE_RECAPTCHA_SITE_KEY")
    app.config["GOOGLE_RECAPTCHA_SECRET_KEY"] = os.environ.get("GOOGLE_RECAPTCHA_SECRET_KEY")

    oauth = OAuth(app)

    # Register Google as an OAuth provider
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    auth = oauth.google

    initialized = True