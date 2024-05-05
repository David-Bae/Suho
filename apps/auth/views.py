from flask import Blueprint, render_template, request, jsonify

#Test용
from apps.crud.models import User
import bcrypt
from datetime import date
from apps.app import db

# 전화 번호 형식 검증
from apps.utils import utils

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
    if utils.validate_phone_number(phone):
        return "유효한 전화 번호입니다."
    else:
        return "유효하지 않는 전화번호입니다."


#! 전화번호가 인증되야 회원가입을 할 수 있음.
@auth.route("/sign-up", methods=['POST'])
def sign_up():
    new_user = request.json
    name = new_user['name']
    phone = new_user['phone']
    birthdate = date(new_user['year'], new_user['month'], new_user['date'])

    # 비밀번호 암호화.
    password_hash = bcrypt.hashpw(
        new_user['password'].encode('UTF-8'),
        bcrypt.gensalt()
    )
    
    user = User(name=name, password_hash=password_hash,
                phone=phone, birthdate=birthdate)

    db.session.add(user)
    db.session.commit()   

    return "회원가입이 완료되었습니다."