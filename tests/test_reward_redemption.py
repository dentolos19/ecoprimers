import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask import session
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from lib.models import Base, Product, Task, Transaction, User
from main import app
from routing.engagement import redeem_reward, tasks_verify


class RewardRedemptionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(
            self.engine,
            tables=[
                Base.metadata.tables[name]
                for name in ("users", "products", "tasks", "transactions")
            ],
        )
        self.db = Session(self.engine, expire_on_commit=False)
        self.db.add_all(
            [
                User(
                    id="alice",
                    email="alice@example.test",
                    name="Alice",
                    password="unused",
                    points=100,
                ),
                Product(id="item", name="Reward", points=60, stock=2),
                Task(
                    id="task",
                    name="Task",
                    description="Description",
                    points=20,
                    criteria="Criteria",
                ),
            ]
        )
        self.db.commit()
        self.previous_secret = app.secret_key
        app.secret_key = "test-secret"
        self.patches = [
            patch("routing.engagement.sql", SimpleNamespace(session=self.db)),
            patch("routing.engagement.env.get", return_value="test-secret"),
            patch(
                "routing.engagement.requests.post",
                return_value=SimpleNamespace(
                    ok=True,
                    json=lambda: {
                        "success": True,
                        "action": "redeem-reward",
                        "hostname": "localhost",
                    },
                ),
            ),
        ]
        for active in self.patches:
            active.start()

    def tearDown(self):
        for active in reversed(self.patches):
            active.stop()
        app.secret_key = self.previous_secret
        self.db.close()
        self.engine.dispose()

    def redeem(self):
        with app.test_request_context(
            "/engagement/redeem/item",
            method="POST",
            data={
                "cf-turnstile-response": "token",
                "reward_cost": "-500",
                "reward_name": "forged",
            },
        ):
            session["user_id"] = "alice"
            self.assertEqual(redeem_reward("item").status_code, 302)

    def test_uses_stored_price_and_prevents_insufficient_redemption(self):
        self.redeem()
        self.assertEqual(self.db.query(User).filter_by(id="alice").one().points, 40)
        self.assertEqual(self.db.query(Product).filter_by(id="item").one().stock, 1)
        transaction = self.db.query(Transaction).one()
        self.assertEqual(transaction.amount, 60)
        self.assertEqual(
            transaction.description, "Points deducted by redeeming reward Reward."
        )

        self.redeem()
        self.assertEqual(self.db.query(User).filter_by(id="alice").one().points, 40)
        self.assertEqual(self.db.query(Product).filter_by(id="item").one().stock, 1)
        self.assertEqual(self.db.query(Transaction).count(), 1)

    def test_rejects_negative_stored_price(self):
        self.db.query(Product).filter_by(id="item").one().points = -1
        self.db.commit()
        self.redeem()
        self.assertEqual(self.db.query(User).filter_by(id="alice").one().points, 100)
        self.assertEqual(self.db.query(Product).filter_by(id="item").one().stock, 2)
        self.assertEqual(self.db.query(Transaction).count(), 0)

    def verify_task(self):
        with (
            patch("routing.engagement.storage.check_format", return_value=True),
            patch("routing.engagement.is_valid_image", return_value=True),
            patch("routing.engagement.load", return_value="{criteria}"),
            patch(
                "routing.engagement.ai.analyze_image",
                return_value={"answer": True, "reasoning": "ok"},
            ),
            patch("routing.engagement.render_template", return_value="status"),
            app.test_request_context(
                "/engagement/tasks/task",
                method="POST",
                data={"image": (io.BytesIO(b"image"), "image.png")},
            ),
        ):
            session["user_id"] = "alice"
            self.assertEqual(tasks_verify("task"), "status")

    def test_task_credit_and_transaction_commit_together(self):
        self.verify_task()
        self.assertEqual(self.db.query(User).filter_by(id="alice").one().points, 120)
        self.assertEqual(self.db.query(Transaction).one().amount, 20)

    def test_task_credit_rolls_back_if_transaction_fails(self):
        with patch.object(self.db, "add", side_effect=SQLAlchemyError("failed")):
            self.verify_task()
        self.assertEqual(self.db.query(User).filter_by(id="alice").one().points, 100)
        self.assertEqual(self.db.query(Transaction).count(), 0)


if __name__ == "__main__":
    unittest.main()
