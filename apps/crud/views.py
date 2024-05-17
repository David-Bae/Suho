from flask import Blueprint, jsonify, request
from apps.auth.views import login_required
from apps.crud import models as DB
from apps.app import db

crud = Blueprint(
    "crud",
    __name__
)

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