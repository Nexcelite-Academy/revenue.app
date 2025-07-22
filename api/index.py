import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app

# Create the Flask application
app = create_app('production')

# Vercel expects this function signature
def handler(request):
    return app(request.environ, request.start_response) 