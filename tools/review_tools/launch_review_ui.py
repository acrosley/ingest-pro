#!/usr/bin/env python3
"""
Launch the review UI in a web browser.
Simple HTTP server to serve the review interface.
"""

import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class ReviewUIHandler(SimpleHTTPRequestHandler):
    """Custom handler to serve the review UI."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        # Add headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress log messages
        pass


def launch_review_ui(port=8000):
    """Launch the review UI in the default web browser."""
    
    # Change to the review_tools directory
    review_tools_dir = Path(__file__).parent
    os.chdir(review_tools_dir)
    
    # Start the server
    server_address = ('', port)
    httpd = HTTPServer(server_address, ReviewUIHandler)
    
    url = f'http://localhost:{port}/review_ui.html'
    
    print("=" * 60)
    print("CALL TRANSCRIPT REVIEW UI")
    print("=" * 60)
    print(f"\n✓ Server started at {url}")
    print(f"✓ Opening review interface in your default browser...")
    print(f"\n📝 Instructions:")
    print(f"  1. Click 'Load Review File' in the browser")
    print(f"  2. Select a .review.json file")
    print(f"  3. Review and correct flagged words")
    print(f"  4. Export corrected transcript when done")
    print(f"\n⚠️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser
    webbrowser.open(url)
    
    # Start serving
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
        sys.exit(0)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Launch the Call Transcript Review UI')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    
    args = parser.parse_args()
    
    launch_review_ui(port=args.port)




