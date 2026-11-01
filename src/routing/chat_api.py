from flask import request, session

from lib import ai
from lib.prompts import load
from main import app


@app.route("/api/chat", methods=["POST"])
def api_chat():
    if not session.get("user_id"):
        return {"error": "Unauthorized"}, 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "Expected a JSON object"}, 400
    prompt = data.get("prompt")
    history = data.get("history")
    if (
        not isinstance(prompt, str)
        or not prompt.strip()
        or not isinstance(history, list)
    ):
        return {"error": "Invalid prompt or history"}, 400
    if any(
        not isinstance(message, dict)
        or not isinstance(message.get("role"), str)
        or not isinstance(message.get("content"), str)
        for message in history
    ):
        return {"error": "Invalid message in history"}, 400

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
