import random
import string
from functools import wraps

from flask import flash, redirect, session, url_for

from main import app_debug


def generate_random_string(length: int = 8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def check_logged_in():
    return ("user_id" in session) or ("user_email" in session)


def require_login(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # Check if the user is logged in
        if check_logged_in():
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return decorator


def require_admin(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # Check if the user is logged in
        if check_logged_in():
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("login"))

        # Skip admin check process if in debug mode
        if app_debug:
            return func(*args, **kwargs)

        # Check if the logged-in user has an admin email
        user_email = session.get(
            "user_email"
        )  # Assuming email is stored in the session during login

        # Check if the user email is an admin email
        if not user_email or not user_email.endswith("@mymail.nyp.edu.sg"):
            flash("Unauthorized access! Admin only.", "danger")
            return redirect(url_for("home"))

        return func(*args, **kwargs)

    return decorator