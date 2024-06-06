from flask import Flask
from routes import order_bp
from database import init_db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    init_db(app)
    app.register_blueprint(order_bp, url_prefix="/api/orders")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
