from datetime import datetime, timedelta
from sqlalchemy import PrimaryKeyConstraint
from apps.app import db

class User(db.Model):
    """
    사용자 기본 정보를 저장하는 베이스 테이블
    """
    __abstract__ = True  # 추상 클래스

    # 필수 입력 정보
    id = db.Column(db.Integer, primary_key=True) # Auto increment
    phone = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    # 선택 입력 정보
    gender = db.Column(db.String(1)) # Male(M), Female(F)
    residence = db.Column(db.String(255))

    def __init__(self, phone, password_hash, name, birthdate, gender=None, residence=None):
        self.phone = phone
        self.password_hash = password_hash
        self.name = name
        self.birthdate = birthdate
        self.gender = gender
        self.residence = residence

class Elder(User):
    """
    고령자 정보를 저장하는 테이블
    """
    __tablename__ = 'elder'
    current_location = db.Column(db.String(255))

    def __init__(self, phone, password_hash, name, birthdate, gender=None, residence=None, current_location=None):
        super().__init__(phone, password_hash, name, birthdate, gender, residence)
        self.current_location = current_location

class Guardian(User):
    """
    보호자 정보를 저장하는 테이블
    """
    __tablename__ = 'guardian'


class CareRelationship(db.Model):
    __tablename__ = 'care_relationship'
    elder_id = db.Column(db.Integer, db.ForeignKey('elder.id'), nullable=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardian.id'), nullable=False)
    elder_to_guardian_relation = db.Column(db.String(50))  # Elder가 Guardian을 어떻게 인식하는지 (예: 아들)
    guardian_to_elder_relation = db.Column(db.String(50))  # Guardian이 Elder를 어떻게 인식하는지 (예: 아버지)

    # 합성키를 primary key로 지정
    __table_args__ = (PrimaryKeyConstraint('elder_id', 'guardian_id'), )

    # 관계를 통한 연결 (SQLAlchemy backref)
    elder = db.relationship('Elder', backref=db.backref('care_relationships', lazy=True))
    guardian = db.relationship('Guardian', backref=db.backref('care_relationships', lazy=True))

    def __init__(self, elder_id, guardian_id, elder_to_guardian_relation=None, guardian_to_elder_relation=None):
        self.elder_id = elder_id
        self.guardian_id = guardian_id
        self.elder_to_guardian_relation = elder_to_guardian_relation
        self.guardian_to_elder_relation = guardian_to_elder_relation


class ConnectionCode(db.Model):
    """
    보호자가 생성하는 '고령자-보호자 연동 코드'
    연동 코드는 보호자 계정으로 생성할 수 있으며,
    연동이 완료되면 연동 코드는 삭제된다. 
    """
    id = db.Column(db.Integer, primary_key=True)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardian.id'), nullable=False)  # Guardian 테이블의 ID 참조
    code = db.Column(db.String(15), unique=True, nullable=False)

    # Guardian 테이블과의 관계 정의
    guardian = db.relationship('Guardian', backref=db.backref('connection_codes', lazy=True))

    def __init__(self, guardian_id, code):
        self.guardian_id = guardian_id
        self.code = code



class Verification(db.Model):
    """
    회원가입시 전화번호 인증을 위한 table
    인증코드가 발송된 후 5분 뒤에 만료도록 구현.
    """
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)  # 인증 코드 만료 시간
    verified = db.Column(db.Boolean, default=False, nullable=False)  # 인증 성공 여부

    def __init__(self, phone, code):
        self.phone = phone
        self.code = code
        self.expiration_time = datetime.utcnow() + timedelta(minutes=5)  # 5분 후 만료
