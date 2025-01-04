import random
import string
from functools import wraps

from flask import flash, redirect, session, url_for


def generate_random_string(length: int = 8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "error")
            return redirect(url_for("login"))

        # Check if the logged-in user has an admin email
        user_email = session.get(
            "user_email"
        )  # Assuming email is stored in the session during login
        if not user_email or not user_email.endswith("@mymail.nyp.edu.sg"):
            flash("Unauthorized access! Admins only.", "error")
            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return decorated_function