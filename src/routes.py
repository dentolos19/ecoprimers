from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import session as db_session
from main import app
from models import User


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


@app.route("/admin/events")
def admin_events():
    return render_template("admin-events.html")


@app.route("/admin/users")
def admin_users():
    return render_template("admin-users.html")


@app.route("/admin/transactions")
def admin_transactions():
    return render_template("admin-transactions.html")


@app.route("/community/messages")
def messaging_page():
    return render_template("messaging.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is already logged in
    if "user_id" in session:
        flash("You're already logged in!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Get the user from the Turso database
        user = db_session.query(User).filter_by(email=email).first()

        # Check if user exists and password matches
        if user and check_password_hash(user.password, password):
            # store user ID in session to keep the user logged in
            session["user_id"] = user.id
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
    session.pop("user_id", None)  # Clear the session
    flash("You've been logged out successfully.", "success")
    return redirect(url_for("home"))