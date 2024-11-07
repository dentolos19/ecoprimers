from flask import render_template

from App import app


# @app.route is basically telling the website what function it should run when you switch to a website.
# in this case, going to the example of placeholder.com/ or placeholder.com/home will both run the home_page() function)
@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")
@app.route("/try1")
def try_out():
    return render_template("try1.html")