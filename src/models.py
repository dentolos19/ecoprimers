from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
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

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    bio: Mapped[str] = mapped_column(nullable=True)
    birthday: Mapped[str] = mapped_column(nullable=True)
    points: Mapped[int] = mapped_column(nullable=False, default=0)


class Event(Base):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)


class EventAttendee(Base):
    __tablename__ = "event_attendees"

    event_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)


class Post(Base):
    __tablename__ = "posts"

    user_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    image_filename: Mapped[str] = mapped_column(nullable=False)


class PostLike(Base):
    __tablename__ = "post_likes"

    post_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)


class PostComment(Base):
    __tablename__ = "post_comments"

    post_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[datetime] = mapped_column(nullable=False)
    task_points: Mapped[int] = mapped_column(nullable=False)


class TaskStatus(Base):
    __tablename__ = "task_status"

    task_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(nullable=False)
    points: Mapped[int] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    user_id: Mapped[int] = mapped_column(nullable=False)  # Foreign key
    type: Mapped[str] = mapped_column(nullable=False)  # "earned" or "redeemed"
    points: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["user_id"] = self.user_id
        base_dict["type"] = self.type
        base_dict["points"] = self.points
        base_dict["description"] = self.description
        return base_dict


class Message(Base):
    __tablename__ = "messages"

    sender_id: Mapped[int] = mapped_column(nullable=False)
    receiver_id: Mapped[int] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)
    is_read: Mapped[bool] = mapped_column(nullable=False, default=False)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["sender_id"] = self.sender_id
        base_dict["receiver_id"] = self.receiver_id
        base_dict["message"] = self.message
        base_dict["is_read"] = self.is_read
        return base_dict


class Donation(Base):
    __tablename__ = "donations"

    username: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    date_time: Mapped[datetime] = mapped_column(nullable=False)