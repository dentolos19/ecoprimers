from flask import render_template, request, session, redirect, url_for
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



@app.route("/community/search-results")
@app.route("/community/messages/<int:receiver_id>", methods=["GET", "POST"])
def search_messages():
    search_query = request.args.get("search_query") 
    valid_messages = (sql.session.query(Message).filter(and_(Message.message.like(f"%{search_query}%"), or_(Message.receiver_id == session["user_id"], Message.sender_id == session["user_id"]))).order_by(Message.created_at).limit(50).all())
    users = sql.session.query(User).all()
    return render_template("search-results.html", messages=[message.to_dict() for message in valid_messages], users = users)

@app.route("/community/messages", methods=["GET"])
def edit_message(id):
    content = request.args.get("new_content")

@app.route("/community/messages/<int:receiver_id>/<int:message_id>", methods=["POST"])
def delete_message(receiver_id, message_id):
    print(receiver_id, message_id)
    
    message = sql.session.query(Message).filter(and_(Message.receiver_id == receiver_id, Message.id == message_id)).first()
    sql.session.delete(message)
    sql.session.commit()
    
    return redirect(url_for("messaging", receiver_id=receiver_id))