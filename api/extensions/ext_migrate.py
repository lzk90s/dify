import flask_migrate
from flask import Flask


def init(app: Flask, db):
    migrations_dir = 'migrations-mysql' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'migrations'
    flask_migrate.Migrate(app, db, directory=migrations_dir)
