import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:p4ssw0rd@localhost/intern_portal"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
