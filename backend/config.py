import os
class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mis.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-me')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
settings = Settings()
