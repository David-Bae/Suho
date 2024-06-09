from flask import Blueprint, jsonify, request
from apps.auth.views import login_required
from apps.crud import models as DB
from apps.app import db
from apps.crud import crud_bp as crud
from apps.crud.jsonify import *

@crud.route("/")
def index():
    return "Hello, CRUD!"

@crud.route("/test", methods=['POST'])
@login_required
def tell_my_name(current_user):
    return jsonify({'message': f'로그인한 사용자 이름은 {current_user.name}입니다.'})


@crud.route("/check-db", methods=['POST'])
def check_db():
    try:
        db.session.add(DB.Dummy())
        db.session.commit()

        return jsonify({'message': 'Database connection successful and data added.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to connect to the database or add data.', 'details': str(e)}), 500

@crud.route("/yuju", methods=['GET'])
def hello_yuju():
    return "Hello, YuJu!"

#! sudo
@crud.route("/add-qa", methods=['POST'])
def add_qa():
    qas = request.json # 여러 개의 질문-답변 쌍을 포함한 리스트

    for qa in qas:
        elder_id = qa['elder_id']
        question = qa['question']
        answer = qa['answer']
        date = qa['date']

        new_qa = DB.QuestionAnswer(elder_id, question, answer, date)
        db.session.add(new_qa)

    db.session.commit()

    return jsonify({'message': '질문-답변이 추가되었습니다.'}), 200


#! sudo
#! 전화번호 인증 없이 회원가입할 수 있는 API.
#! 실제로 사용하는 API 아님.
from datetime import date
import bcrypt

@crud.route("/add-user", methods=['POST'])
def add_user():
    name = request.json['name']
    user_type = request.json['user_type']
    phone = request.json['phone']
    birthdate = request.json['birthdate']
    password = request.json['password']    
    if len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"


    # 비밀번호 암호화
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')


    if user_type == 'E':
        user = DB.Elder(name=name, password_hash=password_hash,
                        phone=phone, birthdate=birthdate)
    else:
        user = DB.Guardian(name=name, password_hash=password_hash,
                        phone=phone, birthdate=birthdate)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': '회원가입이 완료되었습니다.'}), 200


#! 고령자 & 보호자 공통 새로고침 API
@crud.route("/update-all", methods=['GET'])
@login_required
def update_all(current_user):
    response = {
        "SeniorSetting": json_SeniorSetting(current_user),
        "ProtectorSetting": json_ProtectorSetting(current_user),
        "ProtectorInfo": json_ProtectorInfo(current_user),
        "SeniorInfo": json_SeniorInfo(current_user),
        "MessageItem": json_MessageItem(current_user),
        "ScheduleItem": json_ScheduleItem(current_user),
        "MedicineAlarmItem": json_MedicineAlarmItem(current_user),
        "MedicineItem": json_MedicineItem(current_user)
    }

    return jsonify(response), 200
