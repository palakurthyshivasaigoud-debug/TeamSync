import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "teamsync-dev-secret-2024")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///teamsync.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "teamsync-webhook-secret")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
