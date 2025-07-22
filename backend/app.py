from flask import Flask
from flask_cors import CORS
from config.settings import config
from config.database import init_db
import os

def create_app(config_name=None):
    """Application factory pattern"""
    # Configure Flask to serve static files from the 'static' directory
    app = Flask(__name__, static_folder='static', static_url_path='')
    
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
    
    # Database initialization endpoint
    @app.route('/init-db', methods=['POST'])
    def initialize_database():
        try:
            from config.database import init_db
            init_db()
            return {"status": "success", "message": "Database tables created successfully!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
    
    # Sample data seeding endpoint  
    @app.route('/seed-data', methods=['POST'])
    def seed_sample_data():
        try:
            from seed_data import create_sample_data
            create_sample_data()
            return {"status": "success", "message": "Sample data created successfully!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
    
    # Serve frontend
    @app.route('/')
    def serve_frontend():
        return app.send_static_file('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Railway provides PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    
    # Run with Railway-compatible settings
    app.run(
        host='0.0.0.0',  # Railway needs this
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    ) 