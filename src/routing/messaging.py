from flask import redirect, render_template, request, session, url_for
from sqlalchemy import and_, or_

from lib.database import sql
from lib.models import Message, Rooms, User
from lib.socket import notify
from main import app
from utils import require_login


@app.route("/community/messages")
@app.route("/community/messages/<receiver_id>", methods=["GET", "POST"])
@require_login
def messaging(receiver_id=None):
    user_list = sql.session.query(User).all()

    # Find or create the room for this pair so the rooms table stays populated.
    if receiver_id:
        room = (
            sql.session.query(Rooms)
            .filter(
                or_(
                    and_(Rooms.user_1 == session["user_id"], Rooms.user_2 == receiver_id),
                    and_(Rooms.user_1 == receiver_id, Rooms.user_2 == session["user_id"]),
                )
            )
            .first()
        )

        if not room:
            room = Rooms(user_1=session["user_id"], user_2=receiver_id)

            sql.session.add(room)
            sql.session.commit()
            print(f"created room between {room.user_1} and {room.user_2}")

    return render_template(
        "messaging.html",
        users=user_list,
        sender_id=session["user_id"],
        receiver_id=receiver_id,
    )


@app.route("/community/search-results")
@app.route("/community/messages/<receiver_id>", methods=["GET", "POST"])
def search_messages():
    search_query = request.args.get("search_query")
    users = sql.session.query(User).all()
    valid_messages = (
        sql.session.query(Message)
        .filter(Message.is_visible)
        .filter(Message.message.like(f"%{search_query}%"))
        .filter(or_(Message.receiver_id == session["user_id"], Message.sender_id == session["user_id"]))
        .order_by(Message.created_at)
        .limit(50)
        .all()
    )

    return render_template("search-results.html", messages=valid_messages, users=users)


@app.route("/community/messages", methods=["GET"])
def edit_message(id):
    request.args.get("new_content")


@app.route("/community/messages/<receiver_id>/<message_id>", methods=["POST"])
def delete_message(receiver_id, message_id):
    print(receiver_id, message_id)

    message = (
        sql.session.query(Message).filter(and_(Message.receiver_id == receiver_id, Message.id == message_id)).first()
    )

    if message is None:
        return "Message not found", 404

    message.is_visible = False
    sql.session.commit()

    notify(
        message.sender_id,
        message.receiver_id,
        {"type": "message_deleted", "message_id": message_id},
    )

    return redirect(
        url_for("messaging", receiver_id=receiver_id if receiver_id != session["user_id"] else message.sender_id)
    )


@app.route("/community/messages/deleted")
def deleted_messages():
    messages = sql.session.query(Message).filter(
        and_(Message.sender_id == session["user_id"], Message.is_visible.is_(False))
    )
    for message in messages:
        print(message.message)
    return render_template("deleted_messages.html", messages=messages)


@app.route("/community/messages/deleted/restore", methods=["POST"])
def restore_message():
    message_id = request.form.get("message_restoration")
    if not message_id:
        return "No message ID provided", 400  # Handle missing message ID

    message = sql.session.query(Message).filter(Message.id == message_id).first()

    if not message:
        return "Message not found", 404  # Handle missing message

    message.is_visible = True
    sql.session.commit()

    notify(
        message.sender_id,
        message.receiver_id,
        {"type": "message_restored", "message_id": message.id},
    )
    return redirect(url_for("deleted_messages"))  # Redirect after restoring
