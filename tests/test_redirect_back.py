import unittest

from main import app
from utils import redirect_back


class RedirectBackTests(unittest.TestCase):
    def test_only_redirects_to_local_paths(self):
        cases = [
            ("http://localhost/community?tab=saved", "/community?tab=saved"),
            ("https://attacker.example/", "/home"),
            ("http://localhost//attacker.example", "/home"),
            ("http://localhost/\\attacker.example", "/home"),
            (None, "/home"),
        ]
        for referrer, expected in cases:
            headers = {"Referer": referrer} if referrer else {}
            with (
                self.subTest(referrer=referrer),
                app.test_request_context("/", headers=headers),
            ):
                self.assertEqual(redirect_back("/home").headers["Location"], expected)


if __name__ == "__main__":
    unittest.main()
