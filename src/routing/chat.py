from flask import render_template

from main import app
from utils import require_login


@app.route("/chat")
@require_login
def chat():
    return render_template("chat.html")