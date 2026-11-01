import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask import session
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lib.models import Base, Post, User
from main import app
from routing.community import community_delete, community_edit


class CommunityAccessTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        tables = [
            Base.metadata.tables[name]
            for name in ("users", "posts", "post_comments", "post_likes", "post_save")
        ]
        Base.metadata.create_all(self.engine, tables=tables)
        self.db = Session(self.engine, expire_on_commit=False)
        self.db.add_all(
            [
                User(
                    id=name, email=f"{name}@example.test", name=name, password="unused"
                )
                for name in ("alice", "bob")
            ]
            + [Post(id="post", user_id="bob", content="original", shares=0)]
        )
        self.db.commit()
        self.previous_secret = app.secret_key
        app.secret_key = "test-secret"
        self.patches = [
            patch("routing.community.sql", SimpleNamespace(session=self.db)),
            patch("routing.community.render_template", return_value="not found"),
        ]
        for active in self.patches:
            active.start()

    def tearDown(self):
        for active in reversed(self.patches):
            active.stop()
        app.secret_key = self.previous_secret
        self.db.close()
        self.engine.dispose()

    def test_only_author_can_edit_or_delete_a_post(self):
        with app.test_request_context(
            "/community/posts/post", method="POST", data={"content": "changed"}
        ):
            session["user_id"] = "alice"
            self.assertEqual(community_edit("post")[1], 404)
        with app.test_request_context("/community/posts/post/delete", method="POST"):
            session["user_id"] = "alice"
            self.assertEqual(community_delete("post")[1], 404)
        self.assertEqual(
            self.db.query(Post).filter_by(id="post").one().content, "original"
        )
        with app.test_request_context(
            "/community/posts/post", method="POST", data={"content": "updated"}
        ):
            session["user_id"] = "bob"
            self.assertEqual(community_edit("post").status_code, 302)
        self.assertEqual(
            self.db.query(Post).filter_by(id="post").one().content, "updated"
        )
        with app.test_request_context("/community/posts/post/delete", method="POST"):
            session["user_id"] = "bob"
            self.assertEqual(community_delete("post").status_code, 302)
        self.assertIsNone(self.db.get(Post, "post"))


if __name__ == "__main__":
    unittest.main()
