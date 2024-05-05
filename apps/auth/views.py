from flask import Blueprint, render_template, request, jsonify
from apps.crud.models import User, Verification
from datetime import date, datetime, timedelta
from apps.app import db
from apps.utils import utils
import random
import bcrypt

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
    if User.query.filter_by(phone=phone).first() is not None:
        return "이미 등록된 전화번호입니다."

    #! 전화번호 인증
    # 인증코드 생성
    verification_code = str(random.randint(100000, 999999))

    #! 병렬처리.
    # 전화번호로 인증코드 발송
    utils.send_verification_sms(phone, verification_code)
    # DB에 전화번호, 인증코드 저장
    verification = Verification(phone=phone, code=verification_code)
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
    verification = Verification.query.filter_by(phone=phone).order_by(Verification.expiration_time.desc()).first()

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
    verified_record = Verification.query.filter(
        Verification.phone == phone,
        Verification.verified == True,
        Verification.expiration_time >= one_hour_ago
    ).first()

    # 인증된 레코드가 없는 경우 에러 메시지 반환
    if not verified_record:
        return jsonify({'error': '전화번호가 인증되지 않았습니다. 다시 인증 절차를 진행해 주세요.'}), 400

    name = new_user['name']
    birthdate = date(new_user['year'], new_user['month'], new_user['day'])

    # 비밀번호 암호화
    password_hash = bcrypt.hashpw(
        new_user['password'].encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')
    
    user = User(name=name, password_hash=password_hash,
                phone=phone, birthdate=birthdate)

    db.session.add(user)
    db.session.commit()   

    return jsonify({'message': '회원가입이 완료되었습니다.'}), 200


#! 로그인 엔드포인트.
@auth.route("/login", methods=['POST'])
def login():
    if not request.json or 'phone' not in request.json or 'password' not in request.json:
        return jsonify({'error': '전화번호와 비밀번호를 모두 입력해주세요.'}), 400

    login_data = request.json
    phone = login_data['phone']
    password = login_data['password']

    user = User.query.filter_by(phone=phone).first()

    if user is None:
        return jsonify({'error': '해당 사용자가 존재하지 않습니다.'}), 404

    if not bcrypt.checkpw(password.encode('UTF-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': '비밀번호가 틀렸습니다.'}), 401
    
    return jsonify({'message': '로그인 성공!'}), 200