from flask import request, session
from sqlalchemy import and_, or_

from lib.database import sql
from lib.models import Message
from lib.socket import notify
from main import app


@app.route("/api/messages", methods=["GET", "POST"])
def api_messages():
    if request.method == "GET":
        # Get data from search parameters
        sender_id = request.args.get("sender_id")
        receiver_id = request.args.get("receiver_id")
        limit_parameter = request.args.get("limit")
        if limit_parameter:
            try:
                limit = int(limit_parameter)
            except ValueError:
                return {"error": "limit must be an integer"}, 400
        else:
            limit = 50

        # Query messages in the database
        messages = (
            sql.session.query(Message)
            .filter(
                or_(
                    and_(Message.sender_id == sender_id, Message.receiver_id == receiver_id),
                    and_(Message.sender_id == receiver_id, Message.receiver_id == sender_id),
                )
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

        return [message.to_dict() for message in messages]

    if request.method == "POST":
        # The sender is always the logged-in session user, never the request body
        sender_id = session.get("user_id")
        if not sender_id:
            return {"error": "Unauthorized"}, 401

        # Get data from the request
        data: dict = request.get_json(silent=True) or {}
        receiver_id = data.get("receiver_id")
        content = data.get("content")

        if not isinstance(receiver_id, str) or not receiver_id:
            return {"error": "receiver_id is required"}, 400

        if not isinstance(content, str) or not content.strip():
            return {"error": "Message content cannot be empty"}, 400

        # Create a new message
        message = Message(sender_id=sender_id, receiver_id=receiver_id, message=content, is_visible=True)

        # Save the message to the database
        sql.session.add(message)
        sql.session.commit()

        notify(sender_id, receiver_id, {"type": "message", "data": message.to_dict()})

        return message.to_dict(), 201
