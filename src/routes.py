from flask import render_template

from main import app

# Page Routes


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