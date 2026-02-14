import os

from flask import flash, redirect, render_template, request, session, url_for
import resend
from werkzeug.security import check_password_hash, generate_password_hash

from lib import google
from lib.database import sql
from lib.models import User
from main import app

resend.api_key = os.environ.get("RESEND_API_KEY")


def send_welcome_email(user_email):
    resend_from_email = os.environ.get("RESEND_FROM_EMAIL")

    if not resend.api_key or not resend_from_email:
        print("Error sending email: RESEND_API_KEY or RESEND_FROM_EMAIL is missing.")
        return

    params: resend.Emails.SendParams = {
        "from": resend_from_email,
        "to": [user_email],
        "subject": "Welcome to Eco Primers!",
        "html": "<strong>Thank you for signing up for Eco Primers. We are excited to have you on board!</strong>\n<p>Remember to set up your security code in case you forget your password</p>",
    }

    try:
        response: resend.Emails.SendResponse = resend.Emails.send(params)
        print(f"Email sent with ID: {response['id']}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        flash("You're already logged in!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = sql.session.query(User).filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_email"] = user.email

            # Check the email domain
            if user.email.endswith("@mymail.nyp.edu.sg"):
                flash("Admin login successful!", "success")
                return redirect(url_for("admin"))
            else:
                flash("Login successful!", "success")
                return redirect(url_for("home"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


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

            send_welcome_email(new_user.email)

        except Exception as e:
            print(e)
            sql.session.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")
            return redirect(url_for("login"))

    return redirect(url_for("home"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        bio = request.form["bio"]
        birthday = request.form["birthday"]
        security = request.form["security"]  # New security field

        hashed_password = generate_password_hash(password, method="pbkdf2:sha1")

        new_user = User(
            email=email,
            name=name,
            password=hashed_password,
            bio=bio,
            birthday=birthday,
            security=security,  # Save security question
        )

        try:
            sql.session.add(new_user)
            sql.session.commit()
            flash("Sign up successful! You can now log in.", "success")

            send_welcome_email(new_user.email)

            return redirect("/login")

        except Exception as e:
            if "unique constraint" in str(e).lower():
                flash("Error! Email already exists.", "danger")
            sql.session.rollback()
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash("You've been logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        security = request.form["security"]
        new_password = request.form["new_password"]

        # Fetch the user from the database
        user = sql.session.query(User).filter_by(email=email).first()

        if user and user.security == security:
            # Check if the new password is the same as the current one
            if check_password_hash(user.password, new_password):
                flash("New password cannot be the same as the current password.", "danger")
            else:
                # Update the user's password
                user.password = generate_password_hash(new_password, method="pbkdf2:sha1")
                try:
                    sql.session.commit()
                    flash("Password reset successfully. You can now log in.", "success")
                    return redirect("/login")
                except Exception:
                    sql.session.rollback()
                    flash("Error resetting password. Please try again.", "danger")
        else:
            flash("Incorrect email or security answer.", "danger")

    return render_template("reset-password.html")
