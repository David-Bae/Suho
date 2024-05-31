from flask import Blueprint, jsonify, request
from apps.auth.views import login_required
from apps.crud import models as DB
from apps.app import db
from apps.crud import crud_bp as crud

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

@crud.route("/add-qa", methods=['POST'])
def add_qa():
    qas = request.json # 여러 개의 질문-답변 쌍을 포함한 리스트

    for qa in qas:
        elder_id = qa['elder_id']
        guardian_id = qa['guardian_id']
        question = qa['question']
        answer = qa['answer']
        date = qa['date']

        new_qa = DB.QuestionAnswer(elder_id, guardian_id, question, answer, date)
        db.session.add(new_qa)

    db.session.commit()

    return jsonify({'message': '질문-답변이 추가되었습니다.'}), 200

