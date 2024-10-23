from flask import render_template

from app import app


# @app.route is basically telling the website what function it should run when you switch to a website.
# In this case, going to the example of "placeholder.com/" or "placeholder.com/home" will both run this function.
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html.j2")