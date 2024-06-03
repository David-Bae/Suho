from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

from apps.config import DB_URI


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="2AZSMss3p5QPbcY2hBsJ",
        SQLALCHEMY_DATABASE_URI=DB_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)

    Migrate(app, db)

    @app.route('/ping', methods=['GET'])
    def ping():
        return jsonify({'message': 'pong'}), 200

    from apps.crud import crud_bp
    app.register_blueprint(crud_bp, url_prefix="/crud")

    from apps.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from apps.elder import elder_bp
    app.register_blueprint(elder_bp, url_prefix="/elder")

    from apps.guardian import guardian_bp
    app.register_blueprint(guardian_bp, url_prefix="/guardian")

    return app

