from flask import request, jsonify
from apps.app import db
from apps.crud import models as DB
from datetime import date, datetime, timedelta
from apps.auth.views import login_required
from apps.utils.utils import create_connection_code
from apps.utils.common import add_medicine, add_schedule
from apps.utils import report_maker as rp
import json

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




# test_text1 = '''
# 박영미님은 현재 다양한 건강 문제와 가족에 대한 그리움을 경험하고 계시는 \
# 것으로 보입니다. 특히 허리와 다리 통증을 지속적으로 호소하고 있으며, 이는 \
# 일상생활에 영향을 미칠 수 있는 중요한 문제입니다. 건강에 대한 걱정도 여러 \
# 차례 언급되었으며, 이는 신체적 불편함뿐만 아니라 정신적인 스트레스로도 \
# 이어질 수 있습니다. 또한, 박영미님은 손주들과 딸에 대한 강한 애정을 보이\
# 고 계시며, 이들과의 만남을 갈망하고 있습니다. 정서적인 면에서도 가족과의 \
# 연결이 박영미님에게 큰 의미가 있는 것으로 판단됩니다.\
# '''
# test_text2 = '''
# 이러한 상황을 고려할 때, 박영미님의 신체적 건강 관리를 위해 정기적인 의료 \
# 진료를 받으시도록 권장드립니다. 특히, 허리와 다리 통증에 대한 전문적인 평\
# 가와 치료가 필요할 수 있습니다. 또한, 영양가 있는 음식과 적절한 운동을 통\
# 해 건강을 유지할 수 있도록 지원해 주세요. 정서적인 측면에서는 가족과의 교\
# 류를 자주 가질 수 있도록 도움을 주는 것이 좋겠습니다. 가족 방문을 자주 하\
# 거나, 비디오 통화 등을 통해 손주들과의 교류를 활성화하는 방법을 모색해 보\
# 는 것도 좋은 방법이 될 것입니다. 이러한 조치들이 박영미님의 삶의 질을 향\
# 상시키고, 신체적 및 정신적 건강에 긍정적인 영향을 미칠 것입니다.\
# '''

# @guardian.route("/make-report", methods=['POST'])
# def make_report():
#     name = request.json['name']
#     month = request.json['month']
#     filename = 1234
#     args = [name, month, 0, [100,60,100,30], [test_text1, test_text2], filename]
    
#     rp.draw(*args)
#     rp.pdf2img(filename)
    
    
    
#     return jsonify({"message": "done"}), 200