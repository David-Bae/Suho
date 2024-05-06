from flask import Blueprint, render_template, request, jsonify
from apps.crud import models as DB
from datetime import date, datetime, timedelta
from apps.app import db
from apps.utils import utils
import random
import bcrypt
from sqlalchemy.exc import SQLAlchemyError
# jwt
import apps.config as config
import jwt
from functools import wraps

auth = Blueprint(
    "auth",
    __name__
)

@auth.route("/")
def index():
    return "Hello, Auth!"

#! 전화번호 인증 API.
@auth.route("/phone-verification", methods=['POST'])
def phone_verification():
    if not request.json or 'phone' not in request.json:
        return jsonify({'error': 'Bad request'}), 400

    phone = request.json['phone']

    # 전화번호 유효성 검사.
    if utils.validate_phone_number(phone) == False:
        return "유효하지 않는 전화번호입니다."

    # 전화번호 형식 변경 (01012345678 -> 010-1234-5678)
    if len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    
    # 이미 등록된 전화번호인지 확인
    if DB.Elder.query.filter_by(phone=phone).first() is not None or \
       DB.Guardian.query.filter_by(phone=phone).first() is not None:
        return "이미 등록된 전화번호입니다."

    #! 전화번호 인증
    # 인증코드 생성
    verification_code = str(random.randint(100000, 999999))

    #! 병렬처리.
    # 전화번호로 인증코드 발송
    utils.send_verification_sms(phone, verification_code)
    # DB에 전화번호, 인증코드 저장
    verification = DB.Verification(phone=phone, code=verification_code)
    db.session.add(verification)
    db.session.commit()
    
    return jsonify({'message': '인증코드가 성공적으로 발송되었습니다. 입력하신 전화번호로 전송된 인증코드를 입력해 주세요.'}), 200

@auth.route("/verify-code", methods=['POST'])
def verify_code():
    if not request.json or 'phone' not in request.json or 'code' not in request.json:
        return jsonify({'error': 'Bad request'}), 400

    code = request.json['code']
    phone = request.json['phone']
    if len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    # Verification 테이블에서 가장 최근 인증 정보를 가져온다
    verification = DB.Verification.query.filter_by(phone=phone).order_by(DB.Verification.expiration_time.desc()).first()

    if verification is None or verification.code != code or verification.expiration_time < datetime.utcnow():
        return jsonify({'error': '유효하지 않거나 만료된 코드입니다'}), 400
    
    # 인증 성공 시 verified 컬럼 업데이트
    if not verification.verified:
        verification.verified = True
        db.session.commit()

    return jsonify({'message': '전화번호 인증에 성공했습니다.'})


#! 전화번호가 인증되야 회원가입을 할 수 있음.
@auth.route("/sign-up", methods=['POST'])
def sign_up():
    new_user = request.json

    # 전화번호가 인증되었는지 확인
    phone = new_user['phone']
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    # 해당 전화번호로 인증된 최근 1시간 내의 레코드를 조회
    verified_record = DB.Verification.query.filter(
        DB.Verification.phone == phone,
        DB.Verification.verified == True,
        DB.Verification.expiration_time >= one_hour_ago
    ).first()

    # 인증된 레코드가 없는 경우 에러 메시지 반환
    if not verified_record:
        return jsonify({'error': '전화번호가 인증되지 않았습니다. 다시 인증 절차를 진행해 주세요.'}), 400

    user_type = new_user['user_type']
    name = new_user['name']
    birthdate = date(new_user['year'], new_user['month'], new_user['day'])

    # 비밀번호 암호화
    password_hash = bcrypt.hashpw(
        new_user['password'].encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')

    try:
        if user_type == 'E':
            user = DB.Elder(name=name, password_hash=password_hash,
                            phone=phone, birthdate=birthdate)
        else:
            user = DB.Guardian(name=name, password_hash=password_hash,
                            phone=phone, birthdate=birthdate)
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")

    return jsonify({'message': '회원가입이 완료되었습니다.'}), 200


#! 로그인 엔드포인트.
@auth.route("/login", methods=['POST'])
def login():
    if not request.json or 'phone' not in request.json or 'password' not in request.json:
        return jsonify({'error': '전화번호와 비밀번호를 모두 입력해주세요.'}), 400

    login_data = request.json
    phone = login_data['phone']
    password = login_data['password']

    if len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"


    user = DB.Elder.query.filter_by(phone=phone).first()
    if user is None:
        user = DB.Guardian.query.filter_by(phone=phone).first()

    if user is None:
        return jsonify({'error': '해당 사용자가 존재하지 않습니다.'}), 404

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': '비밀번호가 틀렸습니다.'}), 401
    
    user_type = 'E' if type(user) == DB.Elder else 'G'

    #! JWT token
    access_token = jwt.encode({'id': user.id, 'user_type': user_type}, config.JWT_SECRET, algorithm='HS256')

    return jsonify({'message': '로그인 성공!', 'access_token': access_token}), 200


# 인증 decorator 함수
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 요청 헤더에서 token 추출
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        if not token:
            return jsonify({'message': '토큰이 없습니다!'}), 401
        
        try:
            # 토큰 복호화 및 데이터 추출
            data = jwt.decode(token, config.JWT_SECRET, algorithms="HS256")
            if data['user_type'] == 'E':
                current_user = DB.Elder.query.filter_by(id=data['id']).first()
            else:
                current_user = DB.Guardian.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': '토큰이 유효하지 않습니다!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated_function