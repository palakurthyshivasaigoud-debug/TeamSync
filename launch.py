#!/usr/bin/env python3
"""
TeamSync — Quick Launch Script
Starts Flask backend and Streamlit frontend.
"""
import subprocess
import sys
import os
import time
import webbrowser
import threading

# Force UTF-8 stdout if possible
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def check_python():
    if sys.version_info < (3, 9):
        print("[ERROR] Python 3.9+ required. Current:", sys.version)
        sys.exit(1)
    print(f"[OK] Python {sys.version.split()[0]}")


def check_requirements():
    try:
        import flask, streamlit, requests, plotly  # noqa
        print("[OK] Core dependencies verified")
        return True
    except ImportError as e:
        print(f"[WARN] Missing dependency: {e}")
        print("       Run: pip install -r requirements.txt")
        return False


def start_backend():
    print("\n[START] Starting Flask REST API on http://localhost:5000 ...")
    proc = subprocess.Popen(
        [sys.executable, "run_backend.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)
    return proc


def open_browser():
    time.sleep(4)
    try:
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass


def main():
    print("=" * 60)
    print("  TeamSync -- GitHub Engineering & DevOps Platform")
    print("=" * 60)

    check_python()
    if not check_requirements():
        return

    backend_proc = start_backend()

    print("\n[START] Starting Streamlit dashboard on http://localhost:8501 ...")
    print("\n[INFO] Demo Personas Available:")
    print("       - Priya Sharma (Owner & Tech Lead)")
    print("       - Arjun Mehta (Senior Backend Dev)")
    print("       - Sneha Patel (Algorithm Dev - Request Access Demo)")
    print("       - Rohan Gupta (QA & Test Automation Lead)")
    print("\nPress Ctrl+C to stop all services.\n")
    print("-" * 60)

    # Open browser after delay
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
             "--server.headless", "true",
             "--browser.gatherUsageStats", "false"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Stopping TeamSync services...")
    finally:
        backend_proc.terminate()
        print("[OK] All services stopped.")


if __name__ == "__main__":
    main()
