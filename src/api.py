from flask import jsonify, request

from ai import model
from main import app


@app.route("/api/chat", methods=["POST"])
def api_chat():
    # Get the data from the request
    data: dict = request.get_json()
    prompt: str = data["prompt"]
    history: list[dict] = data["history"]

    # Get master prompt
    with open("src/static/masterprompt.txt", "r") as file:
        master_prompt = file.read()

    # Build history context
    ai_request = master_prompt + "\n"
    for message in history:
        role = message["role"]
        message = message["content"]
        ai_request += f"{role}: {message}\n"

    # Add the current prompt to the history
    ai_request += f"user (current prompt): {prompt}\n"

    # Generate a response
    ai_response = model.generate_content(ai_request)
    ai_response_text = ai_response.candidates[0].content.parts[0].text.strip()

    return jsonify({"response": ai_response_text})