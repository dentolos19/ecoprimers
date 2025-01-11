from flask import jsonify, request, render_template

from flask_socketio import join_room
from database import sql
from ai import agent
from main import app, socketio, session
from utils import require_login
from datetime import datetime, timezone
from models import Message, User


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

    return jsonify({"response": ai_response_text})

@app.route('/api/messages', methods=["POST"])
@require_login
def send_message():
    print("Form data received:", request.form)  # Debug print
    message_content = request.form.get("message")
    recipient_id = request.form.get("recepient-id")  # we still get it as recepient-id from the form
    sender_id = request.form.get("sender-id")
    
    if not all([message_content, recipient_id, sender_id]):
        print("Missing required fields:", {
            "message": message_content,
            "recipient_id": recipient_id,
            "sender_id": sender_id
        })
        return "Missing required fields", 400
        
    sent_time = datetime.now(timezone.utc)

    message = Message(
        message=message_content, 
        sender_id=sender_id, 
        receiver_id=recipient_id,  # Changed spelling to match model
        created_at=sent_time, 
        is_read=False
    )
    sql.session.add(message)
    sql.session.commit()

    socketio.emit(
        "receive_message", 
        {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "message": message_content,
            "sent_time": sent_time.isoformat()
        },
        room=recipient_id
    )

    user_list = sql.session.query(User).all()
    return render_template("messaging.html", users=user_list, user_id=session["user_id"])  # Make sure this return statement is always reached

@app.route('/community/messages', methods=["GET"])
@require_login
def get_users():
    pass

    # rest of your code...
# add a socket.io event handler for when users join a chat
@socketio.on('join')
def on_join(data):
    room = data.get('recipient_id')
    if room:
        join_room(room)  # join the room to receive messages

# optionally add disconnect handler
@socketio.on('disconnect')
def on_disconnect():
    pass  # handle any cleanup if needed
