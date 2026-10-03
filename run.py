"""
run.py -- Primary launch entrypoint for Hospital Management System (HMS)
BBAT104 Course Project | Session 2026-27 | CSE-B
Student: Ajay Bora (Roll No: 2410302008)
Baseline System: Hospital Management System
Assigned Quality Goal: Q07 - Improve Data Accuracy

Usage:
    python run.py             # Launches interactive Local Web Application on http://127.0.0.1:5000
    python run.py --desktop   # Launches Desktop GUI (Tkinter) window
"""
import sys
import os
import argparse
import webbrowser
import threading
import time

# Ensure project root and src/ are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from src.database.db_manager import init_db


def launch_web(host="127.0.0.1", port=5000):
    init_db()
    from src.web_app import app

    url = f"http://{host}:{port}"
    print("=" * 65)
    print("  HOSPITAL MANAGEMENT SYSTEM (HMS) - LOCAL WEB SYSTEM")
    print("  BBAT104 TQM Project | Q07: Improve Data Accuracy")
    print("  Student: Ajay Bora | Branch: CSE | Section: B")
    print("=" * 65)
    print(f"\n[+] System is running locally at: {url}")
    print("[+] Opening site in default browser tab...\n")

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host=host, port=port, debug=False)


def launch_desktop():
    init_db()
    from src.main import HMSApp

    print("=" * 65)
    print("  HOSPITAL MANAGEMENT SYSTEM (HMS) - DESKTOP TKINTER GUI")
    print("  BBAT104 TQM Project | Q07: Improve Data Accuracy")
    print("  Student: Ajay Bora | Branch: CSE | Section: B")
    print("=" * 65)
    print("\n[+] Launching Tkinter desktop application window...\n")
    app = HMSApp()
    app.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HMS Application Runner")
    parser.add_argument(
        "--desktop", action="store_true", help="Launch Tkinter desktop GUI instead of web"
    )
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Web server host (default: 127.0.0.1)")
    args = parser.parse_args()

    if args.desktop:
        launch_desktop()
    else:
        launch_web(host=args.host, port=args.port)
