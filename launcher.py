"""
Neuryx Desktop Launcher
Starts the FastAPI backend + opens a native desktop window via pywebview.
"""
import threading
import time
import os
import sys

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def start_server():
    """Run uvicorn in a background thread."""
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
    )


def main():
    # Start backend server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Give the server a moment to boot
    time.sleep(2)

    # Open native window
    import webview
    window = webview.create_window(
        "Neuryx",
        url="http://127.0.0.1:8000",
        width=600,
        height=780,
        resizable=True,
        min_size=(400, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
