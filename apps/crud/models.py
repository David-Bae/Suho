from datetime import datetime

from apps.app import db
#from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True) # Auto increment는 기본 설정
    name = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(255))
    phone = db.Column(db.String(32), unique=True)
    birthdate = db.Column(db.Date, nullable=True)