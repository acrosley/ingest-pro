"""
Corrections Logging API Server

Simple HTTP server that accepts logging requests from the review UI.
Runs locally on port 5555 and logs all actions to the database in real-time.
"""

import json
import logging
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.corrections.corrections_database import (
    log_correction,
    log_approval,
    log_dictionary_addition,
    initialize_database
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Server configuration
HOST = 'localhost'
PORT = 5555


class CorrectionAPIHandler(BaseHTTPRequestHandler):
    """Handle POST requests to log corrections."""
    
    def log_message(self, format, *args):
        """Override to use logger instead of stderr."""
        logger.info("%s - %s" % (self.address_string(), format % args))
    
    def do_OPTIONS(self):
        """Handle preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests."""
        # Parse URL path
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/log':
            self.handle_log_action()
        elif parsed_path.path == '/health':
            self.handle_health_check()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.handle_health_check()
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_health_check(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps({"status": "ok", "service": "corrections-api"})
        self.wfile.write(response.encode())
    
    def handle_log_action(self):
        """Handle logging action."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            action_type = data.get('type')
            
            # Log to database
            if action_type == 'correction':
                log_correction(
                    file_name=data.get('file_name', 'unknown'),
                    word_index=data.get('word_index', 0),
                    original_word=data.get('original_word', ''),
                    corrected_word=data.get('corrected_word', ''),
                    confidence=data.get('confidence'),
                    speaker=data.get('speaker'),
                    context_before=data.get('context_before', ''),
                    context_after=data.get('context_after', ''),
                    flag_types=data.get('flag_types', []),
                    action='corrected'
                )
                logger.info(f"Logged correction: {data.get('original_word')} -> {data.get('corrected_word')}")
                
            elif action_type == 'approval':
                log_approval(
                    file_name=data.get('file_name', 'unknown'),
                    word_index=data.get('word_index', 0),
                    word=data.get('word', ''),
                    confidence=data.get('confidence'),
                    speaker=data.get('speaker'),
                    context_before=data.get('context_before', ''),
                    context_after=data.get('context_after', ''),
                    flag_types=data.get('flag_types', [])
                )
                logger.info(f"Logged approval: {data.get('word')}")
                
            elif action_type == 'dictionary':
                log_dictionary_addition(
                    file_name=data.get('file_name', 'unknown'),
                    term=data.get('term', ''),
                    original_word=data.get('original_word', ''),
                    confidence=data.get('confidence'),
                    was_correction=data.get('was_correction', False)
                )
                logger.info(f"Logged dictionary addition: {data.get('term')}")
                
            else:
                raise ValueError(f"Unknown action type: {action_type}")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = json.dumps({"success": True, "action": action_type})
            self.wfile.write(response.encode())
            
        except Exception as e:
            logger.error(f"Error logging action: {e}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = json.dumps({"success": False, "error": str(e)})
            self.wfile.write(response.encode())


def run_server():
    """Run the corrections API server."""
    # Initialize database
    initialize_database()
    logger.info(f"Database initialized")
    
    # Create server
    server = HTTPServer((HOST, PORT), CorrectionAPIHandler)
    logger.info(f"")
    logger.info(f"=" * 60)
    logger.info(f"Corrections Logging API Server")
    logger.info(f"=" * 60)
    logger.info(f"Listening on: http://{HOST}:{PORT}")
    logger.info(f"Health check: http://{HOST}:{PORT}/health")
    logger.info(f"Log endpoint: http://{HOST}:{PORT}/log")
    logger.info(f"")
    logger.info(f"Keep this window open while reviewing transcripts.")
    logger.info(f"Press Ctrl+C to stop the server.")
    logger.info(f"=" * 60)
    logger.info(f"")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down server...")
        server.shutdown()
        logger.info("Server stopped.")


if __name__ == '__main__':
    run_server()

