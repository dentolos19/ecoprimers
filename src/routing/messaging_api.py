from flask import request
from sqlalchemy import and_, or_

from lib.database import sql
from lib.models import Message
from main import app


@app.route("/api/messages", methods=["GET", "POST"])
def api_messages():
    if request.method == "GET":
        # Get data from search parameters
        sender_id = request.args.get("sender_id")
        receiver_id = request.args.get("receiver_id")
        limit = request.args.get("limit")

        if not limit:
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
        # Get data from the request
        data: dict = request.get_json()
        sender_id: str = data["sender_id"]
        receiver_id: str = data["receiver_id"]
        content: str = data["content"]

        # Create a new message
        message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)

        # Save the message to the database
        sql.session.add(message)
        sql.session.commit()

        return message.to_dict()