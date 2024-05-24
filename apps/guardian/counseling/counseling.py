from apps.guardian import guardian_bp as guardian
from apps.auth.views import login_required
from flask import request, jsonify
from apps.crud import models as DB
from apps.app import db

@guardian.route('/counseling', methods=['GET'])
def index_counseling():
    return "Hello, Counseling!"

@guardian.route('/counseling/add-question', methods=['POST'])
@login_required
def add_question(current_user):
    question_data = request.json
    guardian_id = current_user.id
    """
    사용자 ID는 보안이 필요한 정보는 아님.
    보호자 계정에서 고령자를 조회했을 때,
    서버에서 고령자 ID까지 클라이언트에게 전달하면 됨.
    """
    elder_id = question_data['elder_id']
    question = question_data['question']

    new_question = DB.CustomQuestion(elder_id=elder_id, guardian_id=guardian_id, 
                                     question=question)
    db.session.add(new_question)
    db.session.commit()

    return jsonify({'message': '질문이 등록되었습니다.'}), 200
