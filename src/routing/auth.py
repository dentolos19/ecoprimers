from flask import flash, redirect, session, url_for

from lib import google
from lib.database import sql
from lib.models import User
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
    email: str = user["email"]

    existing_user = sql.session.query(User).filter_by(email=email).first()

    if existing_user:
        # if user already exists, log in
        session["user_id"] = existing_user.id
        session["user_email"] = existing_user.email
        flash("Welcome back! Logged in successfully.", "success")

    else:
        new_user = User(
            email=email,
            name=name,
            password="",
        )

        try:
            sql.session.add(new_user)
            sql.session.commit()

            session["user_id"] = new_user.id
            session["user_email"] = new_user.email
            flash("Account created successfully via Google. Logged in!", "success")
        except Exception as e:
            print(e)
            sql.session.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")
            return redirect(url_for("login"))

    return redirect(url_for("home"))