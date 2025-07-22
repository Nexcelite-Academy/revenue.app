import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_PREFIX = os.environ.get('API_PREFIX', '/api/v1')
    
    # CORS settings
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080').split(',')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tutoring_center.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DEVELOPMENT = False
    
    # For production, require PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Fix for Heroku postgres:// -> postgresql://
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///tutoring_center.db'
    
    # Production security settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

class TestConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
} 