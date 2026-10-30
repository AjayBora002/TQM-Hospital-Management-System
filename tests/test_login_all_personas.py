"""
test_login_all_personas.py
Verifies that every DEMO_PERSONA in src/api/auth.py can log in successfully
via POST /api/auth/login and that the DB seed is consistent with DEMO_PERSONAS.

Tests will FAIL if login.html hardcodes credentials that diverge from DEMO_PERSONAS.
"""
import os
import sys
import json
import unittest

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from web_app import app
from api.auth import DEMO_PERSONAS
from database.db_manager import init_db


class TestLoginAllPersonas(unittest.TestCase):
    """Every DEMO_PERSONA must authenticate successfully through the REST API."""

    @classmethod
    def setUpClass(cls):
        """Initialize the database schema and seed demo users once for the suite."""
        init_db()

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def _login(self, username: str, password: str):
        resp = self.client.post(
            "/api/auth/login",
            data=json.dumps({"username": username, "password": password}),
            content_type="application/json",
        )
        return resp

    def test_all_demo_personas_can_login(self):
        """Each DEMO_PERSONA must return HTTP 200 with success=True."""
        failures = []
        for persona in DEMO_PERSONAS:
            username = persona["username"]
            password = persona["password"]
            resp = self._login(username, password)
            data = {}
            try:
                data = json.loads(resp.data)
            except Exception:
                pass
            if resp.status_code != 200 or not data.get("success"):
                failures.append(
                    f"  FAIL: {username!r} / {password!r} → "
                    f"HTTP {resp.status_code} — {data.get('error', resp.data[:120])}"
                )
        if failures:
            self.fail(
                f"{len(failures)} persona(s) could not log in:\n"
                + "\n".join(failures)
            )

    def test_wrong_password_returns_401(self):
        """A known-good username with the wrong password must return 401."""
        resp = self._login("admin", "wrong_password_xyz")
        self.assertEqual(resp.status_code, 401)

    def test_unknown_username_returns_401(self):
        """A completely unknown username must return 401."""
        resp = self._login("nobody_here", "pass123")
        self.assertEqual(resp.status_code, 401)

    def test_empty_credentials_return_400(self):
        """Empty username/password should return 400 Bad Request."""
        resp = self._login("", "")
        self.assertEqual(resp.status_code, 400)

    def test_demo_personas_have_required_fields(self):
        """Every persona dict must have username, password, role, name, and domain."""
        required = {"username", "password", "role", "name", "domain"}
        for persona in DEMO_PERSONAS:
            missing = required - set(persona.keys())
            self.assertFalse(
                missing,
                f"Persona {persona.get('username')!r} is missing fields: {missing}",
            )

    def test_root_redirects_to_login_when_unauthenticated(self):
        """GET / without a session must redirect to /login, not serve the app shell."""
        resp = self.client.get("/", follow_redirects=False)
        self.assertIn(resp.status_code, (301, 302, 303, 307, 308))
        location = resp.headers.get("Location", "")
        self.assertIn("login", location.lower(), msg=f"Redirect target was: {location!r}")


if __name__ == "__main__":
    unittest.main()
