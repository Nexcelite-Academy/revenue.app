from flask import Flask
from flask_cors import CORS
from config.settings import config
from config.database import init_db
import os

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize CORS for Vercel deployment
    CORS(app, 
         origins=['*'],  # Allow all origins for Vercel
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    # Initialize database
    init_db()
    
    # Register blueprints (routes)
    from api.routes import students, teachers, courses, payments, sessions, expenses, reports
    
    api_prefix = app.config['API_PREFIX']
    app.register_blueprint(students.bp, url_prefix=f"{api_prefix}/students")
    app.register_blueprint(teachers.bp, url_prefix=f"{api_prefix}/teachers")
    app.register_blueprint(courses.bp, url_prefix=f"{api_prefix}/courses")
    app.register_blueprint(payments.bp, url_prefix=f"{api_prefix}/payments")
    app.register_blueprint(sessions.bp, url_prefix=f"{api_prefix}/sessions")
    app.register_blueprint(expenses.bp, url_prefix=f"{api_prefix}/expenses")
    app.register_blueprint(reports.bp, url_prefix=f"{api_prefix}/reports")
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "message": "Tutoring Center API is running"}
    
    # Vercel compatibility
    @app.route('/')
    def index():
        return {"message": "EduManagement API", "status": "running", "version": "1.0.0"}
    
    return app

# For Vercel deployment
app = create_app()

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 