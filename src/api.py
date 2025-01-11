from flask import request
from sqlalchemy import and_

from ai import agent
from database import sql
from main import app
from models import Message


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
    ai_response = agent.generate_content(ai_request)
    ai_response_text = ai_response.candidates[0].content.parts[0].text.strip()

    return {"response": ai_response_text}


@app.route("/api/messages", methods=["GET", "POST"])
def api_messages():
    if request.method == "GET":
        # Get data from search parameters
        sender_id = request.args.get("sender_id")
        receiver_id = request.args.get("receiver_id")
        limit = request.args.get("limit")

        # Query messages in the database
        messages = (
            sql.session.query(Message)
            .filter(
                and_(Message.sender_id == sender_id, Message.receiver_id == receiver_id),
                and_(Message.sender_id == receiver_id, Message.receiver_id == sender_id),
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

        return messages

    if request.method == "POST":
        # Get data from the request
        data: dict = request.get_json()
        sender_id: str = data["sender_id"]
        receiver_id: str = data["receiver_id"]
        content: str = data["content"]

        # Create a new message
        message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        sql.session.add(message)
        sql.session.commit()

        return {"message": "Message sent successfully"}