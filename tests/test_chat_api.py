import unittest
from unittest.mock import patch

from flask import session

from main import app
from routing.chat_api import api_chat


class ChatApiTests(unittest.TestCase):
    def setUp(self):
        self.previous_secret = app.secret_key
        app.secret_key = "test-secret"

    def tearDown(self):
        app.secret_key = self.previous_secret

    @patch("routing.chat_api.ai.generate_text", return_value="response")
    @patch("routing.chat_api.load", return_value="instructions")
    def test_requires_login_and_passes_valid_history(self, load, generate_text):
        payload = {
            "prompt": "new question",
            "history": [{"role": "user", "content": "earlier question"}],
        }
        with app.test_request_context("/api/chat", method="POST", json=payload):
            self.assertEqual(api_chat()[1], 401)
        generate_text.assert_not_called()

        with app.test_request_context("/api/chat", method="POST", json=payload):
            session["user_id"] = "alice"
            self.assertEqual(api_chat(), {"response": "response"})
        self.assertEqual(generate_text.call_args.args[0].count("new question"), 1)
        self.assertIn("earlier question", generate_text.call_args.args[0])
        load.assert_called_once()

    def test_rejects_malformed_history(self):
        with app.test_request_context(
            "/api/chat", method="POST", json={"prompt": "hello", "history": [None]}
        ):
            session["user_id"] = "alice"
            self.assertEqual(api_chat()[1], 400)


if __name__ == "__main__":
    unittest.main()
