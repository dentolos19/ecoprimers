from main import app


@app.route("/api/analysis")
def analysis():
    return "Analysis API"