"""
Launch AssemblyAI Review UI

Opens the AssemblyAI review interface in the default web browser.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path
import threading
import time

def main():
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    ui_file = script_dir / "assemblyai_review_ui.html"
    
    if not ui_file.exists():
        print(f"Error: UI file not found at {ui_file}")
        return 1
    
    # Change to the review tools directory
    os.chdir(script_dir)
    
    # Start server
    PORT = 8002  # Different port from the main review UI
    Handler = http.server.SimpleHTTPRequestHandler
    
    print("=" * 60)
    print("AssemblyAI Transcript Review UI")
    print("=" * 60)
    print(f"\nStarting server on http://localhost:{PORT}")
    print("\nThe review interface will open in your browser shortly...")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{PORT}/assemblyai_review_ui.html")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        return 0
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port {PORT} is already in use.")
            print("The review UI may already be running, or another service is using this port.")
            print(f"You can manually open the UI by navigating to:")
            print(f"file://{ui_file.absolute()}")
        else:
            print(f"\nError starting server: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

