from flask import Blueprint, render_template

# Test용
from apps.crud.models import User
import bcrypt
from datetime import date
from apps.app import db

crud = Blueprint(
    "crud",
    __name__
)

@crud.route("/")
def index():
    return "Hello, CRUD!"

# 더미 데이터 추가 엔드포인트
@crud.route('/add_dummy_data', methods=['GET'])
def add_dummy_data():
    dummy_users = [
        User(name="Alice", password_hash=bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8'), phone="01012345678", birthdate=date(1990, 1, 1)),
        User(name="Bob", password_hash=bcrypt.hashpw(b"password456", bcrypt.gensalt()).decode('utf-8'), phone="01087654321", birthdate=date(1992, 2, 2)),
        User(name="Charlie", password_hash=bcrypt.hashpw(b"password789", bcrypt.gensalt()).decode('utf-8'), phone="01011223344", birthdate=date(1993, 3, 3)),
        User(name="David", password_hash=bcrypt.hashpw(b"password101112", bcrypt.gensalt()).decode('utf-8'), phone="01022334455", birthdate=date(1989, 4, 4)),
        User(name="Eve", password_hash=bcrypt.hashpw(b"password131415", bcrypt.gensalt()).decode('utf-8'), phone="01033445566", birthdate=date(1991, 5, 5))
    ]
    db.session.bulk_save_objects(dummy_users)
    db.session.commit()
    return "Dummy data added successfully!"