import io
import os

import requests
from flask import flash, redirect, render_template, request, send_file, session, url_for
from newsapi.newsapi_exception import NewsAPIException
from PIL import UnidentifiedImageError
from requests.exceptions import RequestException
from sqlalchemy.exc import SQLAlchemyError

from lib import ai, env, storage
from lib.database import sql
from lib.enums import TransactionType
from lib.models import Product, Task, Transaction, User
from lib.prompts import load
from main import app
from utils import require_login


def is_valid_image(file):
    from PIL import Image

    try:
        img = Image.open(io.BytesIO(file.read()))
        img.verify()  # Verify it's an image
        file.seek(0)  # Reset file pointer after reading
        return True
    except (OSError, ValueError, UnidentifiedImageError):
        return False


@app.route("/engagement/tasks")
@require_login
def tasks():
    user_id = session.get("user_id")
    user = sql.session.query(User).filter_by(id=user_id).first()
    tasks = sql.session.query(Task).all()

    return render_template("tasks.html", user=user, tasks=tasks)


@app.route("/engagement/tasks/<id>", methods=["GET", "POST"])
@require_login
def tasks_verify(id):
    task = sql.session.query(Task).filter_by(id=id).first()
    user_id = session.get("user_id")
    user = sql.session.query(User).filter_by(id=user_id).first()

    if task is None:
        return render_template("error.html", error="Task not found"), 404

    if request.method == "POST":
        # Collect data from the form
        image = request.files.get("image")

        # Validate image file
        if not image:
            flash("No image provided.", "danger")
            return redirect(request.url)

        if not storage.check_format(image, storage.image_extensions):
            flash("Invalid file type! Only images (PNG, JPG, JPEG, GIF) are allowed.", "danger")
            return redirect(request.url)

        if not is_valid_image(image):
            flash("Invalid image file! Please upload a valid image.", "danger")
            return redirect(request.url)

        # Get prompt
        prompt = load("verify").format(criteria=task.criteria)

        # Perform verification
        result = ai.analyze_image(
            prompt,
            image.read(),
            image.mimetype or "application/octet-stream",
            return_json=True,
        )

        print("Verification Result:", result)
        print("Answer: " + str(result["answer"]))
        print("Confidence: " + result["reasoning"])

        if result["answer"]:
            if not user:
                print("User not found!")  # Debugging
                flash("User not found!", "danger")
                return redirect(url_for("tasks_verify", id=id))

            print("User Object:", user)  # Debugging
            print("Task Points:", task.points)  # Debugging

            task_points = task.points  # Get points from task model
            task_name = task.name  # Get task name from task model

            try:
                user.points += task_points
                sql.session.commit()
                sql.session.refresh(user)  # Ensure changes are applied

                # Log the transaction
                new_transaction = Transaction(
                    user_id=user_id,
                    type=TransactionType.EARNED,
                    amount=task_points,
                    description=f"Points rewarded for verifying task: {task_name}.",
                )
                sql.session.add(new_transaction)
                sql.session.commit()
                sql.session.refresh(user)  # Ensure changes are applied

                print(f"Points updated successfully! User now has {user.points} points.")  # Debugging
                flash(f"Congratulations! You've earned {task_points} points for {task_name}.", "success")

            except SQLAlchemyError as e:
                sql.session.rollback()
                print("Error while processing points:", str(e))  # Debugging
                flash(f"An error occurred while processing points: {e!s}", "danger")

        return render_template("tasks-verify-status.html", task=task, result=result)

    return render_template("tasks-verify.html", task=task)


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


"""
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
        except SQLAlchemyError as e:
            sql.session.rollback()
            flash(f"An error occurred while processing points: {str(e)}", "danger")
    else:
        flash("User not found!", "danger")

    return redirect(url_for("rewards"))
"""


@app.route("/engagement/redeem/<product_id>", methods=["POST"])
@require_login
def redeem_reward(product_id):
    user_id = session.get("user_id")
    reward_name = request.form.get("reward_name")
    reward_cost_value = request.form.get("reward_cost")
    if reward_cost_value is None:
        flash("Invalid reward details.", "danger")
        return redirect(url_for("rewards"))

    try:
        reward_cost = int(reward_cost_value)
    except ValueError:
        flash("Invalid reward details.", "danger")
        return redirect(url_for("rewards"))

    turnstile_response = request.form.get("cf-turnstile-response")
    if not turnstile_response:
        flash("Complete the security check before redeeming a reward.", "danger")
        return redirect(url_for("rewards"))

    hostname = request.host.split(":", 1)[0]
    data = {
        "secret": env.get("TURNSTILE_SECRET_KEY"),
        "response": turnstile_response,
    }

    remoteip = request.headers.get("CF-Connecting-IP")
    if remoteip:
        data["remoteip"] = remoteip

    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data=data,
            timeout=10,
        )
        result = response.json()
    except (requests.RequestException, ValueError):
        flash("The security check is unavailable. Please try again.", "danger")
        return redirect(url_for("rewards"))

    if (
        not response.ok
        or not result.get("success")
        or result.get("action") != "redeem-reward"
        or not hostname
        or result.get("hostname") != hostname
    ):
        flash("Turnstile verification failed. Please try again.", "danger")
        return redirect(url_for("rewards"))

    # Fetch the user
    user = sql.session.query(User).filter_by(id=user_id).first()

    if user and user.points >= reward_cost:
        try:
            product = sql.session.query(Product).filter_by(id=product_id).first()

            if not product:
                flash("Reward not found!", "danger")
                return redirect(request.referrer)

            if product.stock <= 0:
                flash("Reward is out of stock!", "danger")
                return redirect(request.referrer)

            product.stock -= 1

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
        except SQLAlchemyError as e:
            sql.session.rollback()
            flash(f"An error occurred: {e!s}", "danger")
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


# excel file as database
@app.route("/transactions/export")
def export_transactions():
    import xlsxwriter

    user_id = session.get("user_id")

    # Fetch user transactions
    user_transactions = (
        sql.session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    )

    if not user_transactions:
        return "No transactions found.", 404

    # Convert transactions to a list of dictionaries
    transactions_data = [
        {
            "Date": transaction.created_at.strftime("%d/%m/%Y"),
            "Description": transaction.description,
            "Points": transaction.amount,
            "Type": transaction.type.value,  # Assuming transaction.type is an Enum
        }
        for transaction in user_transactions
    ]

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Transactions")
    header = workbook.add_format({"bold": True})

    columns = list(transactions_data[0])
    for column, name in enumerate(columns):
        worksheet.write(0, column, name, header)
    for row, transaction in enumerate(transactions_data, start=1):
        for column, name in enumerate(columns):
            worksheet.write(row, column, transaction[name])

    workbook.close()

    output.seek(0)

    # Send file as downloadable attachment
    return send_file(
        output,
        as_attachment=True,
        download_name="transactions.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# dashboard at view transaction page
"""#dashboard at view transaction page
@app.route("/transactions/dashboard")
def dashboard():
    user_id = session.get("user_id")

    # Fetch user transactions
    transactions = (
        sql.session.query(Transaction)
        .filter_by(user_id=user_id)
        .order_by(Transaction.created_at.asc())  # Ascending order for line graph
        .all()
    )

    # Check if there are transactions
    # has_transactions = bool(transactions)  # True if transactions exist, False if empty
    # If no transactions, just render the message without graphs
    # if not has_transactions:
    # return render_template("dashboard.html", has_transactions=False)
    # Convert transactions to DataFrame

    df = pd.DataFrame(
        [
            {
                "Date": transaction.created_at.strftime("%Y-%m-%d"),
                "Type": transaction.type.value,
                "Amount": transaction.amount,
            }
            for transaction in transactions
        ]
    )

    # Ensure DataFrame is not empty
    if df.empty:
        return "No data available for visualization.", 404

    # Group data for graphs
    daily_points = df.groupby("Date")["Amount"].sum()  # Line Graph
    transaction_counts = df["Type"].value_counts()  # Bar Graph

    # KPI
    total_earned = df[df["Type"] == "earned"]["Amount"].sum()
    total_redeemed = abs(df[df["Type"] == "redemption"]["Amount"].sum())  # Convert to positive
    net_transactions = total_earned - total_redeemed

    # bar graph
    bar_chart = io.BytesIO()
    plt.figure(figsize=(7, 5))
    transaction_counts.plot(kind="bar", color=["green", "red"])
    plt.title("Most Used Transaction Types")
    plt.xlabel("Transaction Type")
    plt.ylabel("Frequency")
    plt.savefig(bar_chart, format="jpeg")
    plt.close()
    bar_chart.seek(0)
    bar_chart_url = base64.b64encode(bar_chart.getvalue()).decode("utf-8")

    # line graph
    line_chart = io.BytesIO()
    plt.figure(figsize=(7, 5))
    daily_points.plot(kind="line", marker="o", color="blue")
    plt.title("Daily Points Usage")
    plt.xlabel("Date")
    plt.ylabel("Points")
    plt.grid(True)
    plt.savefig(line_chart, format="png")
    plt.close()
    line_chart.seek(0)
    line_chart_url = base64.b64encode(line_chart.getvalue()).decode("utf-8")

    return render_template(
        "dashboard.html",
        bar_chart_url=bar_chart_url,
        line_chart_url=line_chart_url,
        total_earned=total_earned,
        total_redeemed=total_redeemed,
        net_transactions=net_transactions,
    )
"""


@app.route("/transactions/dashboard")
@require_login
def dashboard():
    from collections import defaultdict

    user_id = session.get("user_id")

    # api call for weather app
    # Fetch user transactions
    transactions = (
        sql.session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.created_at.asc()).all()
    )

    if not transactions:
        return "No data available for visualization.", 404

    amounts = [transaction.amount for transaction in transactions]
    dates = [transaction.created_at.strftime("%Y-%m-%d") for transaction in transactions]
    types = [transaction.type.value for transaction in transactions]
    total_earned = sum(amount for amount, transaction_type in zip(amounts, types) if transaction_type == "earned")
    total_redeemed = abs(
        sum(amount for amount, transaction_type in zip(amounts, types) if transaction_type == "redemption")
    )
    net_transactions = total_earned - total_redeemed

    daily_amounts = defaultdict(int)
    for date, amount in zip(dates, amounts):
        daily_amounts[date] += amount

    type_amounts = defaultdict(int)
    for transaction_type, amount in zip(types, amounts):
        type_amounts[transaction_type] += abs(amount)

    daily_totals = list(daily_amounts.values())
    stats = {
        "avg_transaction": sum(amounts) / len(amounts),
        "daily_average": sum(daily_totals) / len(daily_totals),
        "max_transaction": max(amounts),
        "total_transactions": len(transactions),
    }

    return render_template(
        "dashboard.html",
        chart_data={
            "amounts": amounts,
            "dates": list(daily_amounts),
            "daily_amounts": list(daily_amounts.values()),
            "transaction_types": types,
            "type_amounts": dict(type_amounts),
        },
        total_earned=total_earned,
        total_redeemed=total_redeemed,
        net_transactions=net_transactions,
        stats=stats,
    )


# entire news section page
@app.route("/news")
def news():
    from newsapi import NewsApiClient

    newsapi = NewsApiClient(api_key=os.environ.get("NEWS_API_KEY"))

    try:
        environmental_news = newsapi.get_everything(
            q="(climate change OR global warming OR environmental OR sustainability OR "
            "renewable energy OR pollution OR biodiversity OR conservation OR "
            "carbon emissions OR green energy) "
            "-pope -sex -hospital -death -violence -war -sport -game",
            language="en",
            sort_by="publishedAt",
            page_size=12,  # 12 articles for news page
            domains="reuters.com,theguardian.com,bbc.com,nationalgeographic.com,"
            "scientificamerican.com,nature.com,sciencedaily.com,"
            "theconversation.com,sciencenews.org",
        )
        articles = environmental_news["articles"]
    except (NewsAPIException, RequestException, KeyError) as e:
        print(f"Error fetching news: {e}")
        articles = []

    return render_template("news.html", articles=articles)
