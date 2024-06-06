"""
고령자 기본 API를 정의한 모듈
"""

from flask import Blueprint, request, jsonify
from apps.crud import models as DB
from apps.app import db
from datetime import date, datetime, timedelta
from apps.auth.views import login_required
from apps.elder import elder_bp as elder
from apps.utils import utils


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
    if guardian.main_elder_id is None:
        guardian.main_elder_id = current_user.id

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

@elder.route("/toggle-permission", methods=['POST'])
@login_required
def toggle_permmission(current_user):
    elder_id = current_user.id
    guardian_id = request.json['guardian_id']
    permission_type = request.json['permission_type']

    relationship = DB.CareRelationship.query.filter(
        DB.CareRelationship.guardian_id == guardian_id,
        DB.CareRelationship.elder_id == elder_id
    ).first()

    if permission_type == 0:
        relationship.perm_location = False if relationship.perm_location else True
    elif permission_type == 1:
        relationship.perm_schedule = False if relationship.perm_schedule else True
    elif permission_type == 2:
        relationship.perm_message = False if relationship.perm_message else True
    elif permission_type == 3:
        relationship.perm_report = False if relationship.perm_report else True
    else:
        relationship.perm_fall_detect = False if relationship.perm_fall_detect else True

    db.session.commit()

    permission_name = ['위치', '일정', '메시지', '보고서', '낙상감지']

    return jsonify({'message': f"{permission_name[permission_type]}권한이 변경되었습니다."}), 200


@elder.route("/add-medicine", methods=['POST'])
@login_required
def add_medicine_elder(current_user):
    elder_id = current_user.id
    title = request.json['title']

    start_year = request.json['start_year']
    start_month = request.json['start_month']
    start_day = request.json['start_day']
    end_year = request.json['end_year']
    end_month = request.json['end_month']
    end_day = request.json['end_day']

    medicine_period = request.json['medicine_period']  # 0 == 일어나서 1회, 1 == 자기전 1회, 2 == 아침저녁, 3 == 아침점심저녁, 4 == 기타

    memo = request.json['memo']
    do_alarm = request.json['do_alarm']  # 값(n) == n분전 사전알람
    confirm_alarm_minute = request.json['confirm_alarm_minute']  # 값(n) == n분뒤 확인알람

    utils.add_medicine(elder_id=elder_id, title=title, start_year=start_year, start_month=start_month,
                       start_day=start_day, end_year=end_year, end_month=end_month, end_day=end_day,
                       medicine_period=medicine_period, memo=memo, do_alarm=do_alarm, confirm_alarm_minute=confirm_alarm_minute)

    return jsonify({'message': '약이 추가되었습니다.'})
