import stripe
from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import sql
from main import app
from models import Event, User
from utils import check_admin_status, check_logged_in, require_login


@app.context_processor
def init():
    is_logged_in = check_logged_in()
    is_admin_user = check_admin_status()
    return dict(is_logged_in=is_logged_in, is_admin_user=is_admin_user)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    # Query the user from the database
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
        user.username = request.form["username"]
        user.bio = request.form["bio"]
        user.birthday = request.form["birthday"]

        try:
            sql.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect("/profile")
        except Exception as e:
            sql.session.rollback()
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
        user = sql.session.query(User).filter_by(email=email).first()

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
        existing_user = sql.session.query(User).filter((User.email == email) | (User.username == username)).first()

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
            sql.session.add(new_user)
            sql.session.commit()
            flash("Sign up successful! You can now log in.", "success")
            return redirect("/login")
        except Exception as e:
            sql.session.rollback()  # Rollback if there's an error
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
    query = sql.session.query(Event)

    if from_date:
        query = query.filter(Event.date >= from_date)
    if to_date:
        query = query.filter(Event.date <= to_date)
    if location:
        query = query.filter(Event.location == location)

    events = query.all()

    return render_template("events.html", events=events)


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


@app.route("/chat")
@require_login
def chat():
    return render_template("chat.html")


@app.route("/event/details")
def event_info():
    event_id = request.args.get("id")
    event = sql.session.query(Event).filter_by(id=event_id).first()

    return render_template("event-details.html", event=event)


from routing.admin import *
from routing.messaging import *
def transactions():
    return render_template("transaction.html", transactions=user_transactions)
    user_id = session.get("user_id")
    # Fetch all transactions for the user

    user_transactions = db_session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()

@app.route("/add_points", methods=["POST"])
@require_login
def add_points():
    user_id = session.get("user_id")
    task_points = request.form.get("task_points", type=int)  # Get task points from the form
    task_name = request.form.get("task_name")  # Get task name from the form

    
    if not task_points or not task_name:
        flash("Invalid task details provided.", "danger")
        return redirect(url_for("rewards"))
    user = db_session.query(User).filter_by(id=user_id).first()


    if user:
        try:
            user.points += task_points

            # Log the transaction
            new_transaction = Transaction(
                user_id=user_id,
                type="earned",
                points=task_points,
                description=f"Points Gained from completing {task_name}",
                created_at=datetime.utcnow()
            )
            db_session.add(new_transaction)
            db_session.commit()
            flash(f"Congratulations! You've earned {task_points} points for {task_name}.", "success")

        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred while processing points: {str(e)}", "danger")
    else:
        flash("User not found!", "danger")

    return redirect(url_for("rewards"))


@app.route("/redeem_reward", methods=["POST"])
@require_login
def redeem_reward():
    user_id = session.get("user_id")
    reward_name = request.form.get("reward_name")  # Reward name from the form
    reward_cost = int(request.form.get("reward_cost"))  # Reward cost from the form

    # Fetch the user
    user = db_session.query(User).filter_by(id=user_id).first()

    if user and user.points >= reward_cost:
        try:
            # Deduct points from user
            user.points -= reward_cost
            # Log the transaction

            new_transaction = Transaction(
                user_id=user_id,
                type="redeemed",
                points=reward_cost,
                description=f"Redeemed {reward_name}",
            )
                created_at=datetime.utcnow()
            db_session.add(new_transaction)
            db_session.commit()

        except Exception as e:

@app.route("/transactions")


    return redirect(url_for("rewards"))

            flash(f"An error occurred: {str(e)}", "danger")
    else:
            db_session.rollback()
        flash("You do not have enough points to claim this reward!", "danger")
@app.route("/engagement/points")
def points():
    return render_template('points.html')

@app.route("/engagement/rewards")
def rewards():
    user_id = session.get("user_id")
    user = db_session.query(User).filter_by(id=user_id).first()
    return render_template("rewards2.html", user=user)


@app.route("/engagement/task")
def task():
    return render_template('task.html')

