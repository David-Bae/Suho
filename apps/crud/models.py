from datetime import datetime, timedelta

from apps.app import db
#from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True) # Auto increment는 기본 설정
    name = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(255))
    phone = db.Column(db.String(32), unique=True)
    birthdate = db.Column(db.Date, nullable=True)


class Verification(db.Model):
    """
    회원가입시 전화번호 인증을 위한 table
    인증코드가 발송된 후 5분 뒤에 만료도록 구현.
    """
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)  # 인증 코드 만료 시간
    verified = db.Column(db.Boolean, default=False, nullable=False)  # 인증 성공 여부

    def __init__(self, phone, code):
        self.phone = phone
        self.code = code
        self.expiration_time = datetime.utcnow() + timedelta(minutes=5)  # 5분 후 만료
