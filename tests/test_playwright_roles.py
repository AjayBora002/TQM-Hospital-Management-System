"""
test_playwright_roles.py -- Playwright browser verification for HMS
Runs real Chromium browser sessions across multiple roles:
Admin, Doctor, Nurse, Cashier, Patient, Receptionist, Lab Tech, Quality Manager.
Verifies login, navigation, RBAC visibility, topbar readability, hash routing, theme toggling, and mobile drawer.
"""
import os
import sys
import time
import threading
import unittest

# Ensure src is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from web_app import app
from database.db_manager import init_db
from api.auth import DEMO_PERSONAS

from playwright.sync_api import sync_playwright

TEST_PORT = 5055
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


class TestPlaywrightRoles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        os.environ["HMS_DEMO"] = "1"
        cls.server_thread = threading.Thread(
            target=lambda: app.run(host="127.0.0.1", port=TEST_PORT, debug=False, use_reloader=False),
            daemon=True
        )
        cls.server_thread.start()
        time.sleep(1.5)  # Allow Flask server to initialize
        os.makedirs("screenshots", exist_ok=True)

    def test_browser_roles_verification(self):
        """Verify at least 5 different roles in a real browser with Playwright."""
        test_roles = [
            ("admin", "admin123", "Admin"),
            ("doctor", "doctor123", "Doctor"),
            ("nurse", "nurse123", "Nurse"),
            ("cashier", "cash123", "Cashier"),
            ("patient", "patient123", "Patient"),
            ("receptionist", "recep123", "Receptionist"),
            ("lab_tech", "lab123", "Lab Technician"),
            ("quality_mgr", "quality123", "Quality Manager"),
            ("mrd_officer", "mrd123", "MRD Officer"),
            ("telemed_doc", "tele123", "Telemedicine Doctor"),
            ("physiotherapist", "physio123", "Physiotherapist"),
            ("infection_control", "ic123", "Infection Control Nurse"),
            ("security_officer", "sec123", "Security Officer"),
            ("mortuary_attendant", "mort123", "Mortuary Attendant"),
            ("cssd_tech", "cssd123", "CSSD Technician")
        ]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            for username, password, expected_role in test_roles:
                context = browser.new_context(viewport={"width": 1440, "height": 900})
                page = context.new_page()

                console_errors = []
                page.on("console", lambda msg: print(f"[{username}] JS CONSOLE [{msg.type}]: {msg.text}"))
                page.on("pageerror", lambda err: print(f"[{username}] JS PAGE ERROR: {err}"))

                # 1. Unauthenticated root redirects to /login
                page.goto(f"{BASE_URL}/")
                page.wait_for_load_state("networkidle")
                self.assertIn("login", page.url.lower(), f"Unauthenticated request should redirect to /login, got {page.url}")

                # 2. Fill login credentials and submit
                page.fill("#username", username)
                page.fill("#password", password)
                page.click("#submitBtn")

                # Wait for redirect to dashboard
                page.wait_for_url(f"{BASE_URL}/", timeout=10000)
                page.wait_for_load_state("networkidle")
                time.sleep(0.5)

                # 3. Verify user name and role badge in topbar and sidebar
                topbar_role = page.text_content("#currentRoleBadge")
                self.assertIn(expected_role, topbar_role)

                sidebar_user_name = page.text_content("#sidebarUserName")
                self.assertTrue(len(sidebar_user_name.strip()) > 0)

                # 4. Verify role workspace banner rendered on Dashboard (waits for async loadCurrentUser)
                page.wait_for_selector("#roleWorkspaceContainer .role-workspace-banner", timeout=8000)
                workspace_banner = page.locator("#roleWorkspaceContainer .role-workspace-banner")
                self.assertTrue(workspace_banner.count() > 0, f"Role workspace banner missing for {expected_role}")

                # 5. Role-specific module visibility check
                if expected_role == "Patient":
                    # Patient should NOT see EMR, Lab admin, Billing management, etc.
                    emr_btn = page.locator('.nav-item[data-tab="emr"]')
                    if emr_btn.count() > 0:
                        self.assertFalse(emr_btn.is_visible(), "Patient must not see EMR tab")
                    # Patient SHOULD see portal
                    portal_btn = page.locator('.nav-item[data-tab="portal"]')
                    self.assertTrue(portal_btn.is_visible(), "Patient must see portal tab")
                elif expected_role == "Cashier":
                    # Cashier should NOT see EMR
                    emr_btn = page.locator('.nav-item[data-tab="emr"]')
                    if emr_btn.count() > 0:
                        self.assertFalse(emr_btn.is_visible(), "Cashier must not see EMR tab")
                    # Cashier SHOULD see billing
                    billing_btn = page.locator('.nav-item[data-tab="billing"]')
                    self.assertTrue(billing_btn.is_visible(), "Cashier must see billing tab")
                elif expected_role == "Doctor":
                    # Doctor SHOULD see triage, emr, prescriptions, orders
                    emr_btn = page.locator('.nav-item[data-tab="emr"]')
                    self.assertTrue(emr_btn.is_visible(), "Doctor must see EMR tab")
                elif expected_role == "MRD Officer":
                    mrd_btn = page.locator('.nav-item[data-tab="mrd"]')
                    self.assertTrue(mrd_btn.is_visible(), "MRD Officer must see MRD tab")
                    bill_btn = page.locator('.nav-item[data-tab="billing"]')
                    if bill_btn.count() > 0:
                        self.assertFalse(bill_btn.is_visible(), "MRD Officer must not see billing")
                elif expected_role == "Telemedicine Doctor":
                    tele_btn = page.locator('.nav-item[data-tab="telemedicine"]')
                    self.assertTrue(tele_btn.is_visible(), "Telemed Doctor must see telemedicine tab")
                    bill_btn = page.locator('.nav-item[data-tab="billing"]')
                    if bill_btn.count() > 0:
                        self.assertFalse(bill_btn.is_visible(), "Telemed Doctor must not see billing")
                elif expected_role == "Physiotherapist":
                    pt_btn = page.locator('.nav-item[data-tab="physiotherapy"]')
                    self.assertTrue(pt_btn.is_visible(), "Physio must see physiotherapy tab")
                elif expected_role == "Infection Control Nurse":
                    ic_btn = page.locator('.nav-item[data-tab="infection-control"]')
                    self.assertTrue(ic_btn.is_visible(), "Infection nurse must see infection control tab")
                elif expected_role == "Security Officer":
                    sec_btn = page.locator('.nav-item[data-tab="security-log"]')
                    self.assertTrue(sec_btn.is_visible(), "Security officer must see security tab")
                elif expected_role == "Mortuary Attendant":
                    mor_btn = page.locator('.nav-item[data-tab="mortuary"]')
                    self.assertTrue(mor_btn.is_visible(), "Mortuary attendant must see mortuary tab")
                elif expected_role == "CSSD Technician":
                    cssd_btn = page.locator('.nav-item[data-tab="cssd"]')
                    self.assertTrue(cssd_btn.is_visible(), "CSSD technician must see CSSD tab")

                # 6. Test Accordion expansion
                first_header = page.locator(".sidebar-section-header").first
                if first_header.count() > 0 and first_header.is_visible():
                    first_header.click()
                    time.sleep(0.2)

                # 7. Test Hash Routing
                if expected_role in ("Admin", "Doctor"):
                    page.evaluate("window.switchTab('patients')")
                    time.sleep(0.3)
                    self.assertIn("#patients", page.url)

                # 8. Test Dark/Light Theme Toggle
                theme_btn = page.locator("#themeToggleBtn")
                if theme_btn.count() > 0:
                    theme_btn.click()
                    time.sleep(0.2)
                    theme = page.get_attribute("html", "data-theme")
                    self.assertEqual(theme, "dark")
                    theme_btn.click()
                    time.sleep(0.2)
                    theme = page.get_attribute("html", "data-theme")
                    self.assertEqual(theme, "light")

                # 9. Test Command Palette (Ctrl+K)
                page.keyboard.press("Control+KeyK")
                time.sleep(0.3)
                cmd_palette = page.locator("#cmdPaletteOverlay")
                self.assertTrue(cmd_palette.is_visible(), "Command palette should open on Ctrl+K")
                page.keyboard.press("Escape")
                time.sleep(0.2)

                # 10. Take screenshot
                screenshot_path = f"screenshots/role_{username}_desktop.png"
                page.screenshot(path=screenshot_path)
                self.assertTrue(os.path.exists(screenshot_path))

                # Also test tablet (820px) and mobile (390px) for Admin
                if username == "admin":
                    # Tablet 820px
                    page.set_viewport_size({"width": 820, "height": 900})
                    time.sleep(0.3)
                    page.screenshot(path="screenshots/role_admin_tablet_820.png")

                    # Mobile 390px
                    page.set_viewport_size({"width": 390, "height": 844})
                    time.sleep(0.3)
                    # Test mobile hamburger opening
                    page.evaluate("window.toggleSidebar()")
                    time.sleep(0.3)
                    sidebar = page.locator("#appSidebar")
                    self.assertTrue(sidebar.is_visible())
                    page.screenshot(path="screenshots/role_admin_mobile_390.png")

                context.close()

            browser.close()


if __name__ == "__main__":
    unittest.main()
