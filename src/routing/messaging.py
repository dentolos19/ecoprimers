from flask import render_template, request, session
from flask_socketio import join_room

from database import sql
from main import app, socketio
from models import Message, User
from utils import require_login
from sqlalchemy import and_, or_


@socketio.on("join")
def on_join(data):
    room = data.get("receiver_id")
    if room:
        join_room(room)


@socketio.on("disconnect")
def on_disconnect():
    pass


@app.route("/community/messages")
@app.route("/community/messages/<int:receiver_id>", methods=["GET", "POST"])
@require_login
def messaging(receiver_id=None):
    user_list = sql.session.query(User).all()

    if request.method == "POST":
        message_content = request.form.get("message")
        receiver_id = request.form.get("receiver-id")
        sender_id = request.form.get("sender-id")

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message_content,
            is_read=False,
        )

        sql.session.add(message)
        sql.session.commit()

        # socketio.emit(
        #     "receive_message",
        #     message.to_dict(),
        #     room=receiver_id,
        # )

        return render_template(
            "messaging.html",
            users=user_list,
            sender_id=session["user_id"],
            receiver_id=receiver_id,
        )

    return render_template(
        "messaging.html",
        users=user_list,
        sender_id=session["user_id"],
        receiver_id=receiver_id,
    )



@app.route("/community/messages")
@app.route("/community/messages/<int:receiver_id>", methods=["GET", "POST"])
def search_messages():
    search_query = request.args.get("search_query") 
    sql.session.query(Message).filter(and_(Message.message.like(f"%{search_query}%"), or_(Message.receiver_id == session["user_id"], Message.sender_id == session["user_id"]))).all()