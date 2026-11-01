import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask import session
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lib.models import Base, Message, User
from main import app
from routing.messaging import delete_message, restore_message
from routing.messaging_api import api_messages


class MessageAccessTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(
            self.engine,
            tables=[Base.metadata.tables[name] for name in ("users", "messages")],
        )
        self.db = Session(self.engine, expire_on_commit=False)
        self.db.add_all(
            [
                User(
                    id=name, email=f"{name}@example.test", name=name, password="unused"
                )
                for name in ("alice", "bob", "carol")
            ]
            + [
                Message(
                    id="alice-message",
                    sender_id="alice",
                    receiver_id="bob",
                    message="one",
                    is_visible=True,
                ),
                Message(
                    id="bob-message",
                    sender_id="bob",
                    receiver_id="carol",
                    message="two",
                    is_visible=True,
                ),
            ]
        )
        self.db.commit()
        self.previous_secret = app.secret_key
        app.secret_key = "test-secret"
        self.patches = [
            patch("routing.messaging_api.sql", SimpleNamespace(session=self.db)),
            patch("routing.messaging.sql", SimpleNamespace(session=self.db)),
            patch("routing.messaging.notify"),
        ]
        for active in self.patches:
            active.start()

    def tearDown(self):
        for active in reversed(self.patches):
            active.stop()
        app.secret_key = self.previous_secret
        self.db.close()
        self.engine.dispose()

    def test_message_reads_are_limited_to_the_session_user(self):
        url = "/api/messages?sender_id=bob&receiver_id=carol"
        with app.test_request_context(url):
            self.assertEqual(api_messages()[1], 401)
        with app.test_request_context(url):
            session["user_id"] = "alice"
            self.assertEqual(api_messages()[1], 403)
        with app.test_request_context("/api/messages?sender_id=alice&receiver_id=bob"):
            session["user_id"] = "alice"
            self.assertEqual([item["id"] for item in api_messages()], ["alice-message"])

    def test_only_the_sender_can_delete_or_restore(self):
        with app.test_request_context(
            "/community/messages/carol/bob-message", method="POST"
        ):
            session["user_id"] = "alice"
            self.assertEqual(delete_message("carol", "bob-message")[1], 404)
        with app.test_request_context(
            "/community/messages/deleted/restore",
            method="POST",
            data={"message_restoration": "bob-message"},
        ):
            session["user_id"] = "alice"
            self.assertEqual(restore_message()[1], 404)
        self.assertTrue(
            self.db.query(Message).filter_by(id="bob-message").one().is_visible
        )

        with app.test_request_context(
            "/community/messages/bob/alice-message", method="POST"
        ):
            session["user_id"] = "alice"
            self.assertEqual(delete_message("bob", "alice-message").status_code, 302)
        self.assertFalse(
            self.db.query(Message).filter_by(id="alice-message").one().is_visible
        )
        for sender, receiver in (("alice", "bob"), ("bob", "alice")):
            with app.test_request_context(
                f"/api/messages?sender_id={sender}&receiver_id={receiver}"
            ):
                session["user_id"] = sender
                item = api_messages()[0]
                self.assertEqual(item["id"], "alice-message")
                self.assertFalse(item["is_visible"])
                self.assertEqual(item["message"], "")
        with app.test_request_context(
            "/community/messages/deleted/restore",
            method="POST",
            data={"message_restoration": "alice-message"},
        ):
            session["user_id"] = "alice"
            self.assertEqual(restore_message().status_code, 302)
        self.assertTrue(
            self.db.query(Message).filter_by(id="alice-message").one().is_visible
        )
        with app.test_request_context("/api/messages?sender_id=bob&receiver_id=alice"):
            session["user_id"] = "bob"
            self.assertEqual(api_messages()[0]["message"], "one")


if __name__ == "__main__":
    unittest.main()
