import stripe
from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import session as db_session
from environment import STRIPE_SECRET_KEY
from main import app
from models import Event, Transaction, User
from utils import check_admin_status, check_logged_in, require_admin, require_login

stripe.api_key = STRIPE_SECRET_KEY


@app.context_processor
def init():
    is_logged_in = check_logged_in()
    is_admin_user = check_admin_status()
    return dict(is_logged_in=is_logged_in, is_admin_user=is_admin_user)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

from flask import session, redirect, url_for, render_template

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    # Query the user from the database
    user = db_session.query(User).filter(User.id == user_id).first()

    if not user:
        return "User not found", 404

    return render_template("profile.html", user=user)


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login") 

    user = db_session.query(User).filter(User.id == user_id).first()
    
    if request.method == "POST":
        user.email = request.form["email"]
        user.username = request.form["username"]
        user.bio = request.form["bio"]
        user.birthday = request.form["birthday"]

        try:
            db_session.commit()
            flash("Profile updated successfully!", "success")
            return redirect("/profile")
        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
    
    return render_template("edit-profile.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if the user is already logged in
    if "user_id" in session:
        flash("You're already logged in!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Get the user from the database
        user = db_session.query(User).filter_by(email=email).first()

        # Check if user exists and password matches
        if user and check_password_hash(user.password, password):
            # Store user ID in session to keep the user logged in
            session["user_id"] = user.id
            session["user_email"] = user.email  # Store the email in the session

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

        # Check if the username or email already exists in the database
        existing_user = (
            db_session.query(User)
            .filter((User.email == email) | (User.username == username))
            .first()
        )

        if existing_user:
            flash("Error! Username or email already exists.", "danger")
            return redirect("/signup")

        # Hash the password
        hashed_password = generate_password_hash(password, method="pbkdf2:sha1")

        # Create a new user
        new_user = User(
            email=email,
            username=username,
            password=hashed_password,
            bio=bio,
            birthday=birthday,
        )

        try:
            # Add the new user to the database
            db_session.add(new_user)
            db_session.commit()
            flash("Sign up successful! You can now log in.", "success")
            return redirect("/login")
        except Exception as e:
            db_session.rollback()  # Rollback if there's an error
            flash(f"An error occurred: {str(e)}", "danger")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash("You've been logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/events")
@require_login
def events():
    # Get filter values from the request
    from_date = request.args.get("fromDate")
    to_date = request.args.get("toDate")
    location = request.args.get("location")

    # Query the database for events based on filter values
    query = db_session.query(Event)

    if from_date:
        query = query.filter(Event.date >= from_date)
    if to_date:
        query = query.filter(Event.date <= to_date)
    if location:
        query = query.filter(Event.location == location)

    events = query.all()

    return render_template("events.html", events=events)


@app.route("/donation")
@require_login
def donation():
    stripe_session = stripe.checkout.Session.create(
        line_items=[{"price": "price_1QdsnHRxRE93gjFvEyydXEaP", "quantity": 1}],
        mode="payment",
        success_url=url_for("donation_success", _external=True)
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=url_for("donation", _external=True),
    )
    return render_template(
        "donation.html",
        checkout_session_id=stripe_session["id"],
        checkout_public_key=app.config["STRIPE_PUBLIC_KEY"],
    )


@app.route("/donation/success")
@require_login
def donation_success():
    flash("Donation successful! Thank you for your support.", "success")
    return redirect(url_for("donation"))


@app.route("/chat")
@require_login
def chat():
    return render_template("chat.html")


@app.route("/community/messages")
@require_login
def messaging_page():
    return render_template("messaging.html")


@app.route("/admin")
@app.route("/admin/dashboard")
@require_admin
def admin():
    return render_template("admin/dashboard.html")


@app.route("/admin/events", methods=["GET", "POST"])
@require_admin
def admin_events():
    # Query all events from the database
    events = db_session.query(Event).all()

    if request.method == "POST" and request.form.get("delete_event"):
        # Handle deletion of event
        event_id = request.form["delete_event"]
        event_to_delete = db_session.query(Event).filter_by(id=event_id).first()

        if event_to_delete:
            try:
                db_session.delete(event_to_delete)
                db_session.commit()
                flash("Event deleted successfully!", "success")
            except Exception as e:
                db_session.rollback()  # Rollback in case of error
                flash(f"An error occurred while deleting the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events.html", events=events)


@app.route("/admin/events/add", methods=["GET", "POST"])
@require_admin
def admin_events_add():
    if request.method == "POST":
        # Collect data from the form
        event_name = request.form["eventName"]
        event_description = request.form["eventDescription"]
        event_location = request.form["eventLocation"]
        event_date = request.form["eventDate"]

        # Create an Event object and save it to the database
        new_event = Event(
            title=event_name,
            description=event_description,
            location=event_location,
            date=event_date,
        )

        try:
            # Add the event to the session and commit it to the database
            db_session.add(new_event)
            db_session.commit()
            flash("Event added successfully!", "success")
        except Exception as e:
            db_session.rollback()  # Rollback if there's an error
            flash(f"An error occurred while adding the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events-add.html")


@app.route("/admin/users")
@require_admin
def admin_users():
    # Query all events from the database
    users = db_session.query(User).all()

    return render_template("admin/users.html", users=users)


@app.route("/admin/transactions")
@require_admin
def admin_transactions():
    # Query all transactions from the database
    transactions = db_session.query(Transaction).all()

    return render_template("admin/transactions.html", transactions=transactions)