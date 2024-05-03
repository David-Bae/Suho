from flask import Blueprint, render_template, request, jsonify

#Test용
from apps.crud.models import User
import bcrypt
from datetime import date
from apps.app import db

auth = Blueprint(
    "auth",
    __name__
)

@auth.route("/")
def index():
    return "Hello, Auth!"

#! 전화번호 인증 API.
@auth.route("/phone-verification", methods=['GET'])
def phone_verification():
    return "전화번호 인증입니다."


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