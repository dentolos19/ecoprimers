from datetime import date
from importlib import import_module

import stripe
from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from lib.database import sql
from lib.models import Event, EventAttendee, User
from main import app
from utils import check_admin_status, check_logged_in, require_login


@app.context_processor
def init():
    utils = import_module("utils")
    current_date = date.today().isoformat()
    is_logged_in = check_logged_in()
    is_admin_user = check_admin_status()
    return dict(any=any, len=len, utils=utils, current_date=current_date, is_logged_in=is_logged_in, is_admin_user=is_admin_user)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    user = sql.session.query(User).filter(User.id == user_id).first()

    if not user:
        return "User not found", 404

    return render_template("profile.html", user=user)


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    user = sql.session.query(User).filter(User.id == user_id).first()

    if request.method == "POST":
        user.email = request.form["email"]
        user.name = request.form["username"]
        user.bio = request.form["bio"]
        user.birthday = request.form["birthday"]
        user.security = request.form["security"]  # Update security question

        try:
            sql.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect("/profile")
        except Exception as e:
            if "unique constraint" in str(e).lower():
                flash("Error! Username or email already exists.", "danger")
            sql.session.rollback()

    return render_template("edit-profile.html", user=user)


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


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        bio = request.form["bio"]
        birthday = request.form["birthday"]
        security = request.form["security"]  # New security field

        hashed_password = generate_password_hash(password, method="pbkdf2:sha1")

        new_user = User(
            email=email,
            name=username,
            password=hashed_password,
            bio=bio,
            birthday=birthday,
            security=security,  # Save security question
        )

        try:
            sql.session.add(new_user)
            sql.session.commit()
            flash("Sign up successful! You can now log in.", "success")
            return redirect("/login")
        except Exception as e:
            if "unique constraint" in str(e).lower():
                flash("Error! Username or email already exists.", "danger")
            sql.session.rollback()
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash("You've been logged out successfully.", "success")
    return redirect(url_for("home"))

from werkzeug.security import generate_password_hash, check_password_hash

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


@app.route("/events")
@require_login
def events():
    # Get filter values from the request
    from_date = request.args.get("fromDate")
    to_date = request.args.get("toDate")
    location = request.args.get("location")
    search_query = request.args.get("search", "")  # Get the search query if provided

    # Query the database for events based on filter values
    query = sql.session.query(Event)

    if from_date:
        query = query.filter(Event.date >= from_date)
    if to_date:
        query = query.filter(Event.date <= to_date)
    if location:
        query = query.filter(Event.location == location)

    if search_query:
        query = query.filter(Event.title.ilike(f"%{search_query}%") | Event.description.ilike(f"%{search_query}%"))

    events = query.all()
    all_events = sql.session.query(Event).all()

    return render_template("events.html", events=events, all_events=all_events)


@app.route("/donation", methods=["GET", "POST"])
@require_login
def donation():
    if request.method == "POST":
        try:
            amount = int(request.form["amount"]) * 100
            if amount < 50:
                return "Donation amount must be at least $0.50.", 400
        except ValueError:
            return "Invalid donation amount.", 400

        stripe_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "sgd",
                        "product_data": {
                            "name": "Donation",
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=url_for("donation_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("donation", _external=True),
        )

        return redirect(stripe_session.url, code=303)

    return render_template("donation.html")


@app.route("/donation/success")
@require_login
def donation_success():
    flash("Donation successful! Thank you for your support.", "success")
    return redirect(url_for("donation"))


@app.route("/event/details")
def event_info():
    event_id = request.args.get("id")
    event = sql.session.query(Event).filter_by(id=event_id).first()

    return render_template("event-details.html", event=event)


@app.route("/event/signup", methods=["GET", "POST"])
@require_login
def event_signup():
    event_id = request.args.get("id")  # Get event ID from the query parameter
    user_id = session.get("user_id")  # Get the logged-in user's ID from the session

    # Fetch event details from the database
    event = sql.session.query(Event).filter_by(id=event_id).first()
    if not event:
        flash("Event not found", "danger")

    existing_attendee = sql.session.query(EventAttendee).filter_by(event_id=event_id, user_id=user_id).first()
    if existing_attendee:
        flash("You are already signed up for this event.", "info")
        return redirect(url_for("event_info", id=event_id))

    user = sql.session.query(User).filter_by(id=user_id).first()
    if not user:
        flash("User not found", "danger")

    if request.method == "POST":
        try:
            attendee = EventAttendee(event_id=event_id, user_id=user_id)
            sql.session.add(attendee)
            sql.session.commit()
            flash("You have successfully signed up for the event!", "success")
            return redirect(url_for("event_info", id=event_id))
        except Exception as e:
            sql.session.rollback()
            flash(f"Error signing up for the event. Error: {e}", "danger")

    return render_template("event-signup.html", event=event, user=user)


from routing.admin import *
from routing.auth import *
from routing.chat import *
from routing.community import *
from routing.engagement import *
from routing.messaging import *