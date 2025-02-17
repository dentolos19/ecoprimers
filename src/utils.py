import os
import random
import string
from datetime import datetime
from functools import wraps

import requests
from flask import flash, redirect, session, url_for

from lib.database import sql
from lib.models import User


def load_environment():
    from dotenv import load_dotenv

    for file in (".env", "../.env"):
        env = os.path.join(os.getcwd(), file)
        if os.path.exists(env):
            load_dotenv(env)


def generate_random_string(length: int = 8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def to_form_date(date: datetime):
    return date.strftime("%Y-%m-%d")


def from_from_date(date: str):
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_current_user():
    if not check_logged_in():
        return None
    return sql.session.query(User).filter_by(id=session.get("user_id")).first()


def check_logged_in():
    return ("user_id" in session) or ("user_email" in session)


def login_user(user: User):
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_email"] = user.email


def logout_user():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_email", None)


def check_admin_status():
    if not check_logged_in():
        return False
    # TODO: Remove True
    return session.get("user_email").endswith("@mymail.nyp.edu.sg") or True


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


def get_weather_data(location):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()

        rain_chance = data.get("rain", {}).get("2h", 0)

        temperature = data["main"].get("temp", None)

        weather_description = data["weather"][0].get("description", "No description available")

        return {"rain_chance": rain_chance, "temperature": temperature, "weather_description": weather_description}
    else:
        return None