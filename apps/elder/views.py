from flask import Blueprint, request, jsonify
from apps.crud import models as DB
from apps.app import db
from datetime import date, datetime, timedelta
from apps.auth.views import login_required

elder = Blueprint(
    "elder",
    __name__
)

@elder.route("/")
def index():
    return "Hello, elder!"

@elder.route("add-guardian", methods=['POST'])
@login_required
def add_guardian(current_user):
    code = request.json['code']

    connection_code = DB.ConnectionCode.query.filter_by(code=code).first()

    # 연동코드 유효성 검사
    if connection_code is None:
        return jsonify({"error": "연동코드가 유효하지 않습니다."}), 400
    
    # 이미 존재하는 관계인지 확인
    existing_relationship = DB.CareRelationship.query.filter_by(
        elder_id=current_user.id,
        guardian_id=connection_code.guardian_id
    ).first()
    if existing_relationship:
        return jsonify({'error': '이미 등록된 보호자입니다.'}), 409

    # CareRelationship에 추가.
    new_relationship = DB.CareRelationship(elder_id=current_user.id,
                            guardian_id=connection_code.guardian_id)
    db.session.add(new_relationship)
    db.session.commit()

    return jsonify({'message': '보호자가 추가 완료'}), 200
