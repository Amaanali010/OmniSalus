import os
import sys

# 1. Add application directory to sys.path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# 2. Set current working directory
os.chdir(APP_DIR)

# 3. Import Flask application
# Phusion Passenger on cPanel requires a WSGI callable named 'application'
try:
    from app import app as application
except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    
    # Fallback error WSGI app to display debug information on cPanel if startup fails
    def application(environ, start_response):
        status = '500 Internal Server Error'
        output = f"""
        <html>
        <head><title>OmniSalus Startup Error</title></head>
        <body style="font-family: monospace; padding: 2rem; background: #08131f; color: #ff6b6b;">
            <h2>OmniSalus: Application Startup Failed</h2>
            <p style="color: #cbd5e1;">Please check missing dependencies or permissions in cPanel.</p>
            <hr style="border-color: #334155;"/>
            <pre style="background: #0f172a; padding: 1.5rem; border-radius: 8px; color: #fca5a5; overflow-x: auto;">{error_trace}</pre>
        </body>
        </html>
        """.encode('utf-8')
        response_headers = [
            ('Content-type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output]
