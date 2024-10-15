from flask import Flask, render_template

app = Flask(__name__)

# @app.route is basically telling the website what function it should run when you switch to a website. 
# in this case, going to the example of placeholder.com/ or placeholder.com/home will both run the home_page() function)
@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")


if __name__ == "__main__":
    # Debug mode will be turned on via the launch configuration
    app.run()