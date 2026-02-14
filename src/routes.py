from datetime import date

from flask import flash, redirect, render_template, request, session, url_for

from lib import database, payments
from lib.database import sql
from lib.models import Event, EventAttendee, User
from main import app
from utils import check_admin_status, check_logged_in, get_weather_data, require_login


@app.context_processor
def init():
    essentials = dict(
        any=any,
        len=len,
        str=str,
        env=os.environ,
        range=range,
        enumerate=enumerate,
        static=lambda path: url_for("static", filename=path),
    )

    utils = dict(
        current_date=date.today().isoformat(),
        is_logged_in=check_logged_in(),
        is_admin_user=check_admin_status(),
        dark_mode_enabled=session.get("dark_mode", True),
    )

    env = dict(
        GOOGLE_API_KEY=os.environ.get("GOOGLE_API_KEY"),
    )

    return {**essentials, **utils, **env}


@app.errorhandler(404)
def error_notfound(error: Exception):
    return render_template("error.html", error=error)


@app.errorhandler(Exception)
def error_exception(error: Exception):
    return render_template("error.html", error=error)


@app.route("/error/reset", methods=["POST"])
def error_reset():
    database.reset()
    flash("Database reset successfully!", "success")
    return redirect("/")


@app.route("/functions/darkmode")
def toggle_dark_mode():
    session["dark_mode"] = not session.get("dark_mode", True)
    print(session["dark_mode"])
    return redirect(request.referrer)


@app.route("/")
@app.route("/home")
def home():
    articles = []
    news_api = NewsApiClient(api_key="9b8cdb155e0241bf8a3769991f8aa210")

    try:
        news = news_api.get_everything(
            q="(climate change OR global warming OR environmental OR sustainability OR "
            "renewable energy OR pollution OR biodiversity OR conservation OR "
            "carbon emissions OR green energy) "
            "-pope -sex -hospital -death -violence -war -sport -game",
            language="en",
            sort_by="publishedAt",
            page_size=3,
            domains="reuters.com,theguardian.com,bbc.com,nationalgeographic.com,"
            "scientificamerican.com,nature.com,sciencedaily.com,"
            "theconversation.com,sciencenews.org",
        )
        articles = news["articles"]
    except Exception as e:
        print(f"Error fetching news: {e}")

    return render_template("home.html", articles=articles)


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
            amount = float(request.form["amount"])
            if amount < 0.5:
                return "Donation amount must be at least $0.50.", 400
        except ValueError:
            return "Invalid donation amount.", 400

        stripe_session = payments.pay(
            amount, url_for("donation_success", _external=True), url_for("donation", _external=True)
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

    # num of attendees
    attendee_num = len(event.attendees)

    if event:
        location = event.location
        weather_data = get_weather_data(location)

        if weather_data:
            rain_chance = weather_data["rain_chance"]
            temperature = weather_data["temperature"]
            weather_description = weather_data["weather_description"]
        else:
            rain_chance = None
            temperature = None
            weather_description = "Weather data unavailable"

    return render_template(
        "event-details.html",
        event=event,
        rain_chance=rain_chance,
        temperature=temperature,
        weather_description=weather_description,
        attendee_num=attendee_num,
    )


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


@app.route("/event/withdraw", methods=["POST"])
@require_login
def event_withdraw():
    event_id = request.form.get("event_id")
    user_id = session.get("user_id")

    attendee = sql.session.query(EventAttendee).filter_by(event_id=event_id, user_id=user_id).first()
    if not attendee:
        flash("You are not signed up for this event.", "info")
        return redirect(url_for("event_info", id=event_id))

    try:
        sql.session.delete(attendee)
        sql.session.commit()
        flash("You have successfully withdrawn from the event.", "success")
    except Exception as e:
        sql.session.rollback()
        flash(f"Error withdrawing from the event. Error: {e}", "danger")

    return redirect(url_for("event_info", id=event_id))


from routing.admin import *
from routing.admin_api import *
from routing.auth import *
from routing.chat import *
from routing.chat_api import *
from routing.community import *
from routing.engagement import *
from routing.messaging import *
from routing.messaging_api import *
from routing.profile import *
