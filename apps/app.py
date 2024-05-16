from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
        return 'pong'

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    from apps.auth import views as auth_views
    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    from apps.elder import views as elder_views
    app.register_blueprint(elder_views.elder, url_prefix="/elder")

    from apps.guardian import views as guardian_views
    app.register_blueprint(guardian_views.guardian, url_prefix="/guardian")

    return app

