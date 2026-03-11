from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///property_management.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes import main, properties, tenants, leases, maintenance, payments

    app.register_blueprint(main.bp)
    app.register_blueprint(properties.bp)
    app.register_blueprint(tenants.bp)
    app.register_blueprint(leases.bp)
    app.register_blueprint(maintenance.bp)
    app.register_blueprint(payments.bp)

    with app.app_context():
        db.create_all()

    return app
