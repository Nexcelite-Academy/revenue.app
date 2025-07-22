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
    
    # Initialize CORS with explicit configuration
    CORS(app, 
         origins=['http://localhost:8080', 'http://127.0.0.1:8080', 'file://', 'null'],
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
    
    @app.route('/')
    def index():
        return {
            "message": "Tutoring Center Management API", 
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "students": f"{api_prefix}/students",
                "teachers": f"{api_prefix}/teachers", 
                "courses": f"{api_prefix}/courses",
                "payments": f"{api_prefix}/payments",
                "sessions": f"{api_prefix}/sessions",
                "expenses": f"{api_prefix}/expenses",
                "reports": f"{api_prefix}/reports"
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True) 