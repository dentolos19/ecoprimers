import random
import string
from datetime import datetime
from functools import wraps

from flask import flash, redirect, session, url_for

from main import app_debug


def generate_random_string(length: int = 8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def convert_from_form_date(date: str):
    return datetime.strptime(date, "%Y-%m-%d").date()

def convert_to_form_date(date: datetime):
    return date.strftime("%Y-%m-%d")


def check_logged_in():
    return ("user_id" in session) or ("user_email" in session)


def check_admin_status():
    if not check_logged_in():
        return False
    return session.get("user_email").endswith("@mymail.nyp.edu.sg") or app_debug


def require_login(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # Check if the user is logged in
        if not check_logged_in():
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return decorator


def require_admin(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # Check if the user is an admin
        if not check_admin_status():
            flash("Unauthorized access! Admin only.", "danger")
            return redirect(url_for("home"))

        return func(*args, **kwargs)

    return decorator