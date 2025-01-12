from flask import flash, redirect, render_template, request, session, url_for

from database import sql
from main import app
from models import Transaction, User
from utils import require_login


@app.route("/engagement/task")
@require_login
def tasks():
    return render_template("tasks.html")


@app.route("/engagement/rewards")
@require_login
def rewards():
    user_id = session.get("user_id")
    user = sql.session.query(User).filter_by(id=user_id).first()
    return render_template("rewards2.html", user=user)


@app.route("/engagement/points")
@require_login
def points():
    return render_template("points.html")


@app.route("/add_points", methods=["POST"])
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
                type="earned",
                points=task_points,
                description=f"Points Gained from completing {task_name}",
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


@app.route("/redeem_reward", methods=["POST"])
@require_login
def redeem_reward():
    user_id = session.get("user_id")
    reward_name = request.form.get("reward_name")  # Reward name from the form
    reward_cost = int(request.form.get("reward_cost"))  # Reward cost from the form

    # Fetch the user
    user = sql.session.query(User).filter_by(id=user_id).first()

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
            sql.session.add(new_transaction)
            sql.session.commit()

            flash(f"Reward '{reward_name}' claimed successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
    else:
        flash("You do not have enough points to claim this reward!", "danger")

    return redirect(url_for("rewards"))


@app.route("/transactions")
@require_login
def transactions():
    user_id = session.get("user_id")

    # Fetch all transactions for the user
    user_transactions = (
        sql.session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    )

    return render_template("transactions.html", transactions=user_transactions)