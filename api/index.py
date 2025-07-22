#!/usr/bin/env python3
"""
Alternative Vercel API entry point
Route: /api/index.py
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

try:
    from app import create_app
    
    # Create Flask app
    app = create_app('production')
    
    # Export for Vercel
    def handler(environ, start_response):
        return app(environ, start_response)
        
except Exception as e:
    print(f"Error importing Flask app: {e}")
    
    # Fallback simple response
    def handler(environ, start_response):
        response_body = f'API Error: {str(e)}'
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [response_body.encode()] 