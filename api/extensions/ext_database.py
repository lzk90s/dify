from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import get_env

db = SQLAlchemy()
db_type = None


def init_app(app: Flask):
    db.init_app(app)


def is_postgresql() -> bool:
    return get_env('DB_TYPE') == 'postgres'
