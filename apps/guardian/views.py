from flask import request, jsonify
from apps.app import db
from apps.crud import models as DB
from datetime import date, datetime, timedelta
from apps.auth.views import login_required
from apps.utils.utils import create_connection_code
from apps.utils.common import add_medicine, add_schedule
from apps.utils import report_maker as rp
import json
import time

from apps.guardian import guardian_bp as guardian

@guardian.route("/")
def index():
    return "Hello, Guardian!"

@guardian.route('/generate-connection-code', methods=['POST'])
@login_required
def generate_guardian_code(current_user):
    code = create_connection_code()

    # 코드 객체 생성 및 저장
    connection_code = DB.ConnectionCode(guardian_id=current_user.id, code=code)
    db.session.add(connection_code)
    db.session.commit()

    return jsonify({'connection_code': f'{connection_code.code}'}), 200



@guardian.route('/refresh-elders', methods=['GET'])
@login_required
def refresh_elders(current_user):
    #! current_user(보호자)와 연동된 고령자 ID 얻기.
    elder_ids = DB.CareRelationship.query.with_entities(DB.CareRelationship.elder_id).filter(DB.CareRelationship.guardian_id == current_user.id).all()
    elder_ids = [id[0] for id in elder_ids]

    #! Elder 테이블에서 고령자 정보(이름, 전화번호, 생년월일) 가져오기
    elders_data = []
    for id in elder_ids:
        elder = DB.Elder.query.with_entities(DB.Elder.name, DB.Elder.phone, DB.Elder.birthdate).filter(DB.Elder.id == id).first()
        elders_data.append({"id": id ,"name": elder[0], "phone": elder[1], "birthdate": str(elder[2])})

    result = {
        "elders": elders_data,
        "number_of_elders": len(elders_data)
    }

    return jsonify(result), 200


@guardian.route("/get-elder-location", methods=['POST'])
@login_required
def get_elder_location(current_user):
    elder_id = request.json['elder_id']

    location = DB.ElderLocation.query.filter(DB.ElderLocation.elder_id == elder_id).first()

    if location:
        return jsonify({"latitude": location.latitude, "longitude": location.longitude}), 200
    else:
        #! 아직 위치가 업데이트되지 않았으면 (0,0) 반환.
        return jsonify({"latitude": 0.0, "longitude": 0.0})


@guardian.route("/add-medicine", methods=['POST'])
@login_required
def add_medicine_guardian(current_user):
    elder_id = request.json['elder_id']
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

    add_medicine(elder_id=elder_id, title=title, start_year=start_year, start_month=start_month,
                       start_day=start_day, end_year=end_year, end_month=end_month, end_day=end_day,
                       medicine_period=medicine_period, memo=memo, do_alarm=do_alarm, confirm_alarm_minute=confirm_alarm_minute)

    return jsonify({'message': '약이 추가되었습니다.'})


@guardian.route("/add-schedule", methods=['POST'])
@login_required
def add_schedule_guardian(current_user):
    #! 일정 추가 권한 있는지 확인.
    guardian_id = current_user.id
    elder_id = request.json['elder_id']

    perm_schedule = DB.CareRelationship.query.with_entities(
        DB.CareRelationship.perm_schedule
    ).filter(
        DB.CareRelationship.guardian_id == guardian_id,
        DB.CareRelationship.elder_id == elder_id
    ).first()[0]

    if perm_schedule is False:
            return jsonify({'message': '일정 추가 권한이 없습니다.'}), 403

    title = request.json['title']

    start_year = request.json['start_year']
    start_month = request.json['start_month']
    start_day = request.json['start_day']
    start_hour = request.json['start_hour']
    start_minute = request.json['start_minute']

    end_year = request.json['end_year']
    end_month = request.json['end_month']
    end_day = request.json['end_day']
    end_hour = request.json['end_hour']
    end_minute = request.json['end_minute']

    memo = request.json['memo']
    do_alarm = request.json['do_alarm']  # 값(n) == n분전 사전알람
    confirm_alarm_minute = request.json['confirm_alarm_minute']  # 값(n) == n분뒤 확인알람

    add_schedule(
        elder_id=elder_id,
        title=title,
        start_year=start_year,
        start_month=start_month,
        start_day=start_day,
        start_hour=start_hour,
        start_minute=start_minute,
        end_year=end_year,
        end_month=end_month,
        end_day=end_day,
        end_hour=end_hour,
        end_minute=end_minute,
        memo=memo,
        do_alarm=do_alarm,
        confirm_alarm_minute=confirm_alarm_minute
    )

    return jsonify({'message': '일정이 추가되었습니다.'})


@guardian.route("/add-message", methods=['POST'])
@login_required
def add_message(current_user):
    #! 일정 추가 권한 있는지 확인.
    guardian_id = current_user.id
    elder_id = request.json['elder_id']

    perm_message = DB.CareRelationship.query.with_entities(
        DB.CareRelationship.perm_message
    ).filter(
        DB.CareRelationship.guardian_id == guardian_id,
        DB.CareRelationship.elder_id == elder_id
    ).first()[0]

    if perm_message is False:
            return jsonify({'message': '메시지 전달 권한이 없습니다.'}), 403

    title = request.json.get('title')
    year = request.json.get('year')
    month = request.json.get('month')
    day = request.json.get('day')
    hour = request.json.get('hour')
    minute = request.json.get('minute')
    content = request.json.get('content')
    alarm_type = request.json.get('alarm_type')

    if not all([elder_id, title, year, month, day, hour, minute, content, alarm_type is not None]):
        return jsonify({'message': '데이터가 부족합니다.'}), 400

    new_message = DB.Message(
        elder_id=elder_id,
        guardian_id=guardian_id,
        title=title,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        content=content,
        alarm_type=alarm_type
    )
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': '메시지가 추가되었습니다.'}), 200

@guardian.route("/change-main-elder", methods=["POST"])
@login_required
def change_main_elder(current_user):
    elder_id = request.json['elder_id']
    
    guardian = DB.Guardian.query.filter(
        DB.Guardian.id == current_user.id
    ).first()
    
    guardian.main_elder_id = elder_id
    db.session.commit()
    
    return jsonify({"message": "main 고령자를 변경하였습니다."}), 200

@guardian.route("/fall-detection", methods=["GET"])
@login_required
def fall_detection_guardian(current_user):
    elder = db.session.query(DB.Elder).filter(DB.Elder.id == current_user.main_elder_id).first()
    
    if elder.fall_detect:
        elder.fall_detect = False
        db.session.commit()
        return jsonify({"message": 1}), 200
    else:
        return jsonify({"message": 0}), 200
    
    # for i in range(300):
        
        
    #     if elder.fall_detect:
    #         elder.fall_detect = False
    #         db.session.commit()
    #         return jsonify({"message": 1}), 200
        
    #     db.session.commit()
    #     time.sleep(1)

    # return jsonify({"message": 0}), 200