from flask import redirect, url_for

from lib import google
from main import app


@app.route("/login/google")
def login_google():
    redirect = url_for("login_authorize", _external=True)
    return google.auth.authorize_redirect(redirect)


@app.route("/login/authorize")
def login_authorize():
    token = google.auth.authorize_access_token()
    user = google.auth.parse_id_token(token, nonce=None)

    name: str = user["name"]
    first_name: str = user["given_name"]
    last_name: str = user["family_name"]
    email: str = user["email"]
    picture: str = user["picture"]

    print(name)

    # TODO: Match with our database

    return redirect("/")