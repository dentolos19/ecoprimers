import uuid

from flask import render_template, request, session, redirect, url_for
from flask_socketio import join_room

from lib.database import sql
from lib.models import Message, User, Rooms
from main import app, socket
from utils import require_login
from sqlalchemy import and_, or_ 


@socket.on("join")
def on_join(data):
        room = sql.session.query(Rooms).filter(
        or_(
            and_(Rooms.user_1 == session["user_id"], Rooms.user_2 == data.get("receiver_id")),
            and_(Rooms.user_1 == data.get("receiver_id"), Rooms.user_2 == session["user_id"])
        )
        ).first()
        
        if not room:
            room = Rooms(room_id = str(uuid.uuid4()), user_1 = session["user_id"], user_2 = data.get("receiver_id"))

            sql.session.add(room)
            sql.session.commit()
            print(f"created room between {room.user_1} and {room.user_2}")

        join_room(room.room_id)

        print(f"joined room between {room.user_1} and {room.user_2}")

@app.route("/community/messages")
@app.route("/community/messages/<receiver_id>", methods=["GET", "POST"])
@require_login
def messaging(receiver_id=None):
    user_list = sql.session.query(User).all()

    return render_template(
        "messaging.html",
        users=user_list,
        sender_id=session["user_id"],
        receiver_id=receiver_id,
    )


@socket.on("send_message")
def handle_send_message(data):
    sender_id = session["user_id"]
    receiver_id = data.get("receiver_id")
    message_content = data.get("message")

    # Save the message in the database
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message_content,
        is_read=False,
    )
    sql.session.add(message)
    sql.session.commit()

    room_id = receiver_id  
    socket.emit("receive_message", message.to_dict(), room=room_id)




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
    
    return redirect(url_for("messaging", receiver_id=receiver_id if receiver_id != session["user_id"] else message.sender_id))