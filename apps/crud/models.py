from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from sqlalchemy import PrimaryKeyConstraint, Date, Float
from apps.app import db
from apps.utils import utils

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

    """
    고령자가 매일 어떤 설문을 해야할지에 대한 정보를 저장한 Column
    0: 신체적 건강, 1: 정신 건강, 2: 사회적 건강, 3: 생활습관
    update_counseling_type() 함수로 업데이트할 수 있음.
    """
    counseling_type = db.Column(db.Integer, nullable=False)

    def __init__(self, phone, password_hash, name, birthdate, gender=None, residence=None, current_location=None):
        super().__init__(phone, password_hash, name, birthdate, gender, residence)
        self.current_location = current_location
        self.counseling_type = 0

    def update_counseling_type(self):
        counseling_types = [0, 1, 2, 3]
        # 현재 상담 유형을 순환시켜서 다음 유형으로 업데이트
        self.counseling_type = (self.counseling_type + 1) % len(counseling_types)
        db.session.commit()

class CounselingScore(db.Model):
    """
    고령자가 수행한 검사(상담) 점수를 저장하는 테이블
    """
    __tablename__ = 'counseling_score'
    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('elder.id'), nullable=False)
    counseling_type = db.Column(db.Integer, nullable=False)
    date = db.Column(Date, nullable=False)
    score = db.Column(Float, nullable=False)

    def __init__(self, elder_id, counseling_type, score):
        self.elder_id = elder_id
        self.counseling_type = counseling_type
        self.score = score
        self.date = date.today()


class MonthlyEvaluation(db.Model):
    """
    고령자가 수행한 검사(상담) 월별 평가가 저장된 테이블
    """
    __tablename__ = "monthly_evaluation"

    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('elder.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)

    physical_score = db.Column(db.Float)    # 0
    mental_score = db.Column(db.Float)      # 1
    social_score = db.Column(db.Float)      # 2
    lifestyle_score = db.Column(db.Float)   # 3

    #! 한 달에 하나의 월별 평가만 존재
    __table_args__ = (
        db.UniqueConstraint('elder_id', 'month', name='unique_elder_month'),
    )

    #! 평가를 하지 않은 항목은 None
    def __init__(self, elder_id, month, physical_score=None, 
                 mental_score=None, social_score=None, lifestyle_score=None):
        self.elder_id = elder_id
        self.month = month
        self.physical_score = physical_score
        self.mental_score = mental_score
        self.social_score = social_score
        self.lifestyle_score = lifestyle_score



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
    """
    __tablename__ = 'phone_verification_code'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    valid_date = db.Column(db.Date, nullable=False, default=date.today)  # 유효 날짜 및 시간
    verified = db.Column(db.Boolean, default=False, nullable=False)  # 인증 성공 여부

    def __init__(self, phone, code):
        self.phone = phone
        self.code = code
        self.valid_date = date.today()

class Dummy(db.Model):
    """
    DB 연결을 확인하기 위한 Dummy 테이블
    """
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime(timezone=True),
                     default=utils.get_current_time_seoul(), nullable=False)

class CustomQuestion(db.Model):
    """
    보호자가 등록한 개인적인 질문들
    """
    __tablename__ = 'custom_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('elder.id'), nullable=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardian.id'), nullable=False)
    question = db.Column(db.String(256), nullable=False)

    def __init__(self, elder_id, guardian_id, question):
        self.elder_id = elder_id
        self.guardian_id = guardian_id
        self.question = question

class QuestionAnswer(db.Model):
    """
    보호자가 등록한 개인적인 질문들에 대한 답변
    """
    __tablename__ = 'question_answer'
    
    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('elder.id'), nullable=False)
    #guardian_id = db.Column(db.Integer, db.ForeignKey('guardian.id'), nullable=False) #! 여러명의 보호자가 질문한 것 한번에 처리.
    question = db.Column(db.String(256), nullable=False)
    answer = db.Column(db.String(256))
    date = db.Column(Date, nullable=False)
    #! 0:angry, 1:disgust, 2:fear, 3:happy, 4:neutral, 5:sad
    emotion = db.Column(db.Integer)

    def __init__(self, elder_id, question, answer=None, date=datetime.today()):
        self.elder_id = elder_id
        self.question = question
        self.answer = answer
        self.date = date
        
class ElderLocation(db.Model):
    """
    고령자 실시간 위치를 저장하는 테이블
    """    
    __tablename__ = 'elder_location'
    
    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('elder.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    def __init__(self, elder_id, latitude, longitude):
        self.elder_id = elder_id
        self.latitude = latitude
        self.longitude = longitude