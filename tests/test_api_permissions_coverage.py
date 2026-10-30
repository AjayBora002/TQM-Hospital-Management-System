"""
test_api_permissions_coverage.py
Walks app.url_map and asserts that every /api/* route is guarded
with @require_permission (or is explicitly on the auth whitelist).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from web_app import app
from database.db_manager import init_db


class TestApiPermissionsCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_all_api_routes_have_permissions_or_whitelisted(self):
        """Every API endpoint must have @require_permission or be on the strict whitelist."""
        whitelist = {
            "static",
            "index",
            "login_page",
            "about_page",
            "auth.login",
            "auth.logout",
            "auth.get_demo_accounts",
            "auth.get_current_session_info",
            "auth.current_user",
            "auth.change_password",
        }

        unprotected_endpoints = []
        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            if endpoint in whitelist:
                continue

            # Check if this is an API route or page route
            if rule.rule.startswith("/api/"):
                view_func = app.view_functions.get(endpoint)
                if not view_func:
                    continue

                # Check if decorated with require_permission
                has_permission_guard = (
                    hasattr(view_func, "_required_permission") or
                    hasattr(getattr(view_func, "__wrapped__", None), "_required_permission") or
                    "_required_permission" in getattr(view_func, "__dict__", {})
                )

                if not has_permission_guard:
                    unprotected_endpoints.append(f"{rule.rule} [{endpoint}]")

        self.assertEqual(
            unprotected_endpoints,
            [],
            f"The following API routes lack @require_permission:\n" + "\n".join(unprotected_endpoints)
        )


if __name__ == "__main__":
    unittest.main()
