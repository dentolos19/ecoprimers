import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    username: Mapped[str]  # TODO: Rename to "name"
    points: Mapped[int] = mapped_column(default=0)
    bio: Mapped[Optional[str]]
    birthday: Mapped[Optional[str]]  # TODO: Use datetime

    posts: Mapped[List["Post"]] = relationship()
    transactions: Mapped[List["Transaction"]] = relationship()


class Event(Base):
    __tablename__ = "events"

    title: Mapped[str]
    description: Mapped[str]
    location: Mapped[str]
    date: Mapped[str]
    image_filename: Mapped[Optional[str]]

    attendees: Mapped[List["EventAttendee"]] = relationship()


class EventAttendee(Base):
    __tablename__ = "event_attendees"

    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str]  # e: "interested" or "withdrawn"

    event = relationship("Event", back_populates="attendees")


class Post(Base):
    __tablename__ = "posts"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    description: Mapped[str]
    image_filename: Mapped[Optional[str]]

    user = relationship("User", back_populates="posts")
    likes: Mapped[List["PostLike"]] = relationship()
    comments: Mapped[List["PostComment"]] = relationship()


class PostLike(Base):
    __tablename__ = "post_likes"

    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    post = relationship("Post", back_populates="likes")


class PostComment(Base):
    __tablename__ = "post_comments"

    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str]

    post = relationship("Post", back_populates="comments")


class Task(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    description: Mapped[datetime]  # TODO: Why datetime?
    task_points: Mapped[int]


class TaskStatus(Base):
    __tablename__ = "task_status"

    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str]  # e: "completed" or "pending"


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str]
    points: Mapped[int]
    stock: Mapped[int]


class Transaction(Base):
    __tablename__ = "transactions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str]  # e: "earned" or "redeemed"
    points: Mapped[int]
    description: Mapped[str]

    user: Mapped[User] = relationship("User", back_populates="transactions")

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["user_id"] = self.user_id
        base_dict["type"] = self.type
        base_dict["points"] = self.points
        base_dict["description"] = self.description
        return base_dict


class Message(Base):
    __tablename__ = "messages"

    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str]
    is_read: Mapped[bool] = mapped_column(default=False)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["sender_id"] = self.sender_id
        base_dict["receiver_id"] = self.receiver_id
        base_dict["message"] = self.message
        base_dict["is_read"] = self.is_read
        return base_dict


# NOTE: I think maybe better to move to "Transactions" for all types of transactions (e.g., points, donations, etc.)
class Donation(Base):
    __tablename__ = "donations"

    username: Mapped[str]  # TODO: Change to user relationship
    amount: Mapped[float]
    date_time: Mapped[datetime]  # NOTE: Don't need use, have "created_at" in base class


class Room(Base):
    tablename = "rooms"

    user_1: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user_2: Mapped[str] = mapped_column(ForeignKey("users.id"))