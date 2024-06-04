from flask import request, jsonify
from apps.app import db
from apps.crud import models as DB
from datetime import date, datetime, timedelta
from apps.auth.views import login_required
from apps.utils.utils import create_connection_code
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


@guardian.route("/get-elder-location", methods=['GET'])
@login_required
def get_elder_location(current_user):
    elder_id = request.json['elder_id']
    
    location = DB.ElderLocation.query.filter(DB.ElderLocation.elder_id == elder_id).first()
    
    if location:    
        return jsonify({"latitude": location.latitude, "longitude": location.longitude}), 200
    else:
        #! 아직 위치가 업데이트되지 않았으면 (0,0) 반환.
        return jsonify({"latitude": 0.0, "longitude": 0.0})