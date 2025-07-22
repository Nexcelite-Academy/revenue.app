#!/usr/bin/env python3
"""
Vercel-specific entry point for the Flask application
This ensures proper serverless function deployment
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# Create the Flask app for Vercel
app = create_app('production')

# Vercel entry point
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, request.start_response)

# For direct invocation
if __name__ == "__main__":
    app.run(debug=False) 