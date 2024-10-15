from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")


if __name__ == "__main__":
    # Debug mode will be turned on via the launch configuration
    app.run()

# hasdbfiauw