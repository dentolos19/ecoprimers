from flask import request

from lib import ai
from lib.prompts import load
from main import app


@app.route("/api/chat", methods=["POST"])
def api_chat():
    # Get the data from the request
    data: dict = request.get_json()
    prompt: str = data["prompt"]
    history: list[dict] = data["history"]

    # Get master prompt
    master_prompt = load("customer-service")

    # Build history context
    ai_request = master_prompt + "\n"
    for message in history:
        role = message["role"]
        message = message["content"]
        ai_request += f"{role}: {message}\n"

    # Add the current prompt to the history
    ai_request += f"user (current prompt): {prompt}\n"

    # Generate a response
    ai_response = ai.generate_text(ai_request)

    return {"response": ai_response}
