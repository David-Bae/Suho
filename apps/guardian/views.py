from flask import request, jsonify
from apps.app import db
from apps.crud import models as DB
from datetime import date, datetime, timedelta
from apps.auth.views import login_required
from apps.utils.utils import create_connection_code

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

    return jsonify({'message': f'연동 코드: {connection_code.code}'}), 200