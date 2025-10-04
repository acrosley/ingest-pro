"""
Launch Transcript Correction UI
Simple HTTP server for the correction tool
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 8080

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler with CORS enabled for local file access"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    # Change to the correction_ui directory
    correction_ui_dir = Path(__file__).parent
    os.chdir(correction_ui_dir)
    
    print("=" * 60)
    print("  📝 Transcript Correction Tool")
    print("=" * 60)
    print(f"\n✅ Server starting on port {PORT}...")
    print(f"📂 Serving from: {correction_ui_dir}")
    
    try:
        with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
            url = f"http://localhost:{PORT}/index.html"
            print(f"\n🌐 Opening browser at: {url}")
            print("\n📋 Features:")
            print("  - Load confidence JSON and audio files")
            print("  - Edit words by clicking flagged highlights")
            print("  - Change speaker names by clicking speaker labels")
            print("  - Search for specific words")
            print("  - Adjust confidence threshold with slider")
            print("  - Export corrected transcript (Ctrl+S)")
            print("\n⌨️  Keyboard Shortcuts:")
            print("  - Space: Play/Pause audio")
            print("  - Ctrl+S: Export transcript")
            print("  - Esc: Close modals")
            print("\n🛑 Press Ctrl+C to stop the server\n")
            print("=" * 60)
            
            # Open browser
            webbrowser.open(url)
            
            # Start server
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {PORT} is already in use.")
            print(f"   Try closing other applications or changing PORT in launch.py")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

