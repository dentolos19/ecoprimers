from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, Event
from database import session as db_session

from main import app

# Page Routes


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/admin")
def admin():
    return render_template("admin-dashboard.html")


@app.route("/admin/events", methods=["GET", "POST"])
def admin_events():
    if request.method == "POST":
        # Collect data from the form
        event_name = request.form['eventName']
        event_description = request.form['eventDescription']
        event_location = request.form['eventLocation']
        event_date = request.form['eventDate']

        # Create an Event object and save it to the database
        new_event = Event(
            title=event_name,
            description=event_description,
            location=event_location,
            date=event_date
        )

        try:
            # Add the event to the session and commit it to the database
            db_session.add(new_event)
            db_session.commit()
            flash("Event added successfully!", 'success')
        except Exception as e:
            db_session.rollback()  # Rollback if there's an error
            flash(f"An error occurred while adding the event: {str(e)}", 'error')

        return redirect(url_for('admin_events'))

    return render_template("admin-events.html")


@app.route("/admin/users")
def admin_users():
    return render_template("admin-users.html")


@app.route("/admin/transactions")
def admin_transactions():
    return render_template("admin-transactions.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # check if user is already logged in
    if 'user_id' in session:
        flash("You're already logged in!", 'error')
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # get the user from the Turso database
        user = db_session.query(User).filter_by(email=email).first()

        # check if user exists and password matches
        if user and check_password_hash(user.password, password):
            # store user ID in session to keep the user logged in
            session['user_id'] = user.id
            flash("Login successful!", 'success')  
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password. Please try again.", 'error')

    return render_template("login.html")

# Sign-up route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        bio = request.form['bio']
        birthday = request.form['birthday']


        # Check if the username or email already exists in the database
        existing_user = db_session.query(User).filter((User.email == email) | (User.username == username)).first()

        if existing_user:
            flash("Error! Username or email already exists.", 'error')
            return redirect('/signup')

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha1')

        # Create a new user
        new_user = User(email=email, username=username, password=hashed_password, bio=bio, birthday=birthday)

        try:
            # Add the new user to the database
            db_session.add(new_user)
            db_session.commit()
            flash('Sign up successful! You can now log in.', 'success')
            return redirect('/login')
        except Exception as e:
            db_session.rollback()  # Rollback if there's an error
            flash(f"An error occurred: {str(e)}", 'error')

    return render_template("signup.html")


# Logout route
@app.route("/logout")
def logout():
    session.pop('user_id', None)  # Clear the session
    flash("You've been logged out successfully.", 'success')
    return redirect(url_for("home"))

@app.route("/events")
def events():
    # Query the database for all events
    events = db_session.query(Event).all()

    return render_template("events.html", events=events)