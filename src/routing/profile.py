from flask import flash, redirect, render_template, request, session

from lib.database import sql
from lib.models import Event, EventAttendee, Post, Transaction, User, UserFollow
from main import app
from utils import require_login


@app.route("/profile")
@require_login
def profile():
    user_id = session.get("user_id")
    user = sql.session.query(User).filter(User.id == user_id).first()
    events = sql.session.query(Event).join(EventAttendee).filter(EventAttendee.user_id == user_id).all()
    posts = sql.session.query(Post).filter(Post.user_id == user_id).all()
    followers = sql.session.query(UserFollow).filter(UserFollow.user_id == user_id).count()
    followings = sql.session.query(UserFollow).filter(UserFollow.follower_id == user_id).count()
    transactions = sql.session.query(Transaction).filter(Transaction.user_id == user_id).count()

    return render_template(
        "profile.html",
        user=user,
        events=events,
        posts=posts,
        followers=followers,
        followings=followings,
        transactions=transactions,
        editable=True,
    )


@app.route("/profile/<id>")
def profile_other(id):
    user = sql.session.query(User).filter(User.id == id).first()
    events = sql.session.query(Event).join(EventAttendee).filter(EventAttendee.user_id == id).all()
    posts = sql.session.query(Post).filter(Post.user_id == id).all()
    followers = sql.session.query(UserFollow).filter(UserFollow.user_id == id).count()
    followings = sql.session.query(UserFollow).filter(UserFollow.follower_id == id).count()
    transactions = sql.session.query(Transaction).filter(Transaction.user_id == id).count()

    return render_template(
        "profile.html",
        user=user,
        events=events,
        posts=posts,
        followers=followers,
        followings=followings,
        transactions=transactions,
    )


@app.route("/profile/edit", methods=["GET", "POST"])
@require_login
def profile_edit():
    user_id = session.get("user_id")
    user = sql.session.query(User).filter(User.id == user_id).first()

    if request.method == "POST":
        user.email = request.form["email"]
        user.name = request.form["name"]
        user.bio = request.form["bio"]
        user.birthday = request.form["birthday"]
        user.security = request.form["security"]  # Update security question

        try:
            sql.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect("/profile")
        except Exception as e:
            if "unique constraint" in str(e).lower():
                flash("Error! Email already exists.", "danger")
            sql.session.rollback()

    return render_template("profile-edit.html", user=user)