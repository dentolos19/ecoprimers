import requests
from flask import flash, redirect, render_template, request, session, url_for

from lib.database import sql
from lib.enums import TransactionType
from lib.models import Product, Transaction, User
from main import app
from utils import require_login


@app.route("/engagement/task")
@require_login
def tasks():
    user_id = session.get("user_id")
    user = sql.session.query(User).filter_by(id=user_id).first()
    return render_template("tasks.html", user=user)


@app.route("/engagement/rewards")
@require_login
def rewards():
    user_id = session.get("user_id")
    user = sql.session.query(User).filter_by(id=user_id).first()
    products = sql.session.query(Product).all()
    return render_template("rewards.html", user=user, products=products)


@app.route("/engagement/points")
@require_login
def points():
    user_id = session.get("user_id")
    user = sql.session.query(User).filter_by(id=user_id).first()
    return render_template("points.html", user=user)


@app.route("/engagement/points/add", methods=["POST"])
@require_login
def add_points():
    user_id = session.get("user_id")
    task_points = request.form.get("task_points", type=int)  # Get task points from the form
    task_name = request.form.get("task_name")  # Get task name from the form

    if not task_points or not task_name:
        flash("Invalid task details provided.", "danger")
        return redirect(url_for("rewards"))

    user = sql.session.query(User).filter_by(id=user_id).first()

    if user:
        try:
            user.points += task_points

            # Log the transaction
            new_transaction = Transaction(
                user_id=user_id,
                type=TransactionType.EARNED,
                amount=task_points,
                description=f"Points rewarded to user by completing task {task_name}.",
            )
            sql.session.add(new_transaction)
            sql.session.commit()

            flash(f"Congratulations! You've earned {task_points} points for {task_name}.", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while processing points: {str(e)}", "danger")
    else:
        flash("User not found!", "danger")

    return redirect(url_for("rewards"))


RECAPTCHA_SECRET_KEY = "6Ldk8skqAAAAAPZgQrYfsfwoOGHQJ5z0q5ZNC4l5"


@app.route("/engagement/redeem", methods=["POST"])
@require_login
def redeem_reward():
    user_id = session.get("user_id")
    reward_name = request.form.get("reward_name")
    reward_cost = int(request.form.get("reward_cost"))

    # Verify reCAPTCHA
    recaptcha_response = request.form.get("g-recaptcha-response")  # Get response from form
    recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"

    payload = {
        "secret": RECAPTCHA_SECRET_KEY,  # Your Google reCAPTCHA secret key
        "response": recaptcha_response,
    }

    response = requests.post(recaptcha_verify_url, data=payload)
    result = response.json()

    if not result.get("success"):
        flash("reCAPTCHA verification failed. Please try again.", "danger")
        return redirect(url_for("rewards"))

    # Fetch the user
    user = sql.session.query(User).filter_by(id=user_id).first()

    if user and user.points >= reward_cost:
        try:
            # Deduct points from user
            user.points -= reward_cost

            # Log the transaction
            new_transaction = Transaction(
                user_id=user_id,
                type=TransactionType.REDEMPTION,
                amount=reward_cost,
                description=f"Points deducted by redeeming reward {reward_name}.",
            )
            sql.session.add(new_transaction)
            sql.session.commit()

            flash(f"Reward '{reward_name}' claimed successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
    else:
        flash("You do not have enough points to claim this reward!", "danger")

    return redirect(url_for("rewards"))


@app.route("/engagement/transactions")
@require_login
def transactions():
    user_id = session.get("user_id")

    # Fetch all transactions for the user
    user_transactions = (
        sql.session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    )

    return render_template("transactions.html", transactions=user_transactions)