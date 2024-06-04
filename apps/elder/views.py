"""
고령자 기본 API를 정의한 모듈
"""

from flask import Blueprint, request, jsonify
from apps.crud import models as DB
from apps.app import db
from datetime import date, datetime, timedelta
from apps.auth.views import login_required
from apps.elder import elder_bp as elder


@elder.route("/", methods=['GET'])
def index():
    return "Hello, elder!"

@elder.route("/add-guardian", methods=['POST'])
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
    
    guardian = DB.Guardian.query.filter_by(id=connection_code.guardian_id).first()

    # CareRelationship에 추가.
    new_relationship = DB.CareRelationship(elder_id=current_user.id,
                            guardian_id=connection_code.guardian_id)
    db.session.add(new_relationship)
    db.session.commit()

    return jsonify({'message': '보호자 추가 완료',
                    'guardian_name': guardian.name,
                    'guardian_phone': guardian.phone}), 200

@elder.route("/update-location", methods=['POST'])
@login_required
def update_location(current_user):
    elder_id = current_user.id
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    
    elder_location = DB.ElderLocation.query.filter(DB.ElderLocation.elder_id == elder_id).first()
    
    if elder_location:
       elder_location.latitude = latitude
       elder_location.longitude = longitude 
    else:
        elder_location = DB.ElderLocation(elder_id, latitude=latitude, longitude=longitude)
        db.session.add(elder_location)
        
    db.session.commit()
    
    return jsonify({'message': "위치가 업데이트 되었습니다."}), 200