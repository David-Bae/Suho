from apps.elder import elder_bp as elder
from apps.auth.views import login_required
from apps.crud import models as DB
from flask import request, jsonify
import os
import json


"""
정형화된 검사가 저장된 디렉토리
절대주소를 사용하는게 안전하다.
"""
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
COUNSELING_FILE_DIR = os.path.join(current_directory, 'questionnaires')

@elder.route("/counseling", methods=['GET'])
def index_counseling():
    return "Hello, Counseling!"


@elder.route("/daily-counseling", methods=['GET'])
@login_required
def get_daily_counseling(current_user):
    """
    정형화된 검사 전체를 반환하는 API
    """

    elder = DB.Elder.query.filter_by(id=current_user.id).first()
    elder.update_counseling_type()

    return jsonify({'message': f'Counseling Type: {elder.counseling_type}'}), 200

    """
    file_path = os.path.join(COUNSELING_FILE_DIR, 'lifestyle/survey.json')

    #return jsonify({'FILE_PATH': f'{file_path}'}), 200

    with open(file_path, 'r') as file:
        counseling_data = json.load(file)

    return jsonify(counseling_data), 200
    """


@elder.route("/daily-question", methods=['GET'])
@login_required
def get_daily_question(current_user):
    """
    보호자가 등록한 질문을 반환하는 API
    """

    return jsonify({'message': f'ID: {current_user.id}'}), 200