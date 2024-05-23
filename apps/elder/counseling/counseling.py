from apps.elder import elder_bp as elder
from apps.auth.views import login_required
from apps.crud import models as DB
from apps.app import db
from flask import request, jsonify
from sqlalchemy import func, text
import os
import json


#####################################################################################
"""
정형화된 검사가 저장된 디렉토리
절대주소를 사용하는게 안전하다.
"""
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
COUNSELING_FILE_DIR = os.path.join(current_directory, 'questionnaires')
COUNSELING_NAME = ['0_physical_health', '1_mental_health', '2_social_health', '3_lifestyle']
#####################################################################################



@elder.route("/counseling", methods=['GET'])
def index_counseling():
    return "Hello, Counseling!"


@elder.route("/daily-counseling", methods=['POST'])
@login_required
def get_daily_counseling(current_user):
    """
    정형화된 검사 전체를 반환하는 API
    """

    elder = DB.Elder.query.filter_by(id=current_user.id).first()

    file_path = os.path.join(COUNSELING_FILE_DIR, COUNSELING_NAME[elder.counseling_type],'survey.json')

    with open(file_path, 'r') as file:
        counseling_data = json.load(file)

    return jsonify(counseling_data), 200



"""
정형화된 검사를 점수화 하는 함수
Input: 객관식 답변 배열.
Output: 점수 (실수)
각 항목에 하나의 함수가 존재한다.
"""
def evaluate_physical_health(answers):
    score = answers[0] * 0.33 + answers[1] + answers[2] * 0.33 + \
            answers[3] + answers[4] + answers[5]
    if score > 5.9:
        score = 100.0
    else:
        score = score / 6 * 100
    return round(score, 1)

def evaluate_mental_health(answers):
    score = 11.0 + sum(answers)
    if 43.9 < score < 44.1:
        score = 100.0
    else:
        score = score / 44 * 100
    return round(score, 1)

def evaluate_social_health(answers):
    score = sum(answers)
    score = score / 3 * 10

    return round(score, 1)

def evaluate_lifestyle(answers):
    score = sum(answers[:2]) * 0.25 + sum(answers[2:7]) + sum(answers[7:10]) * 0.5
    score *= 10
    return round(score, 1)

#! 점수화 함수 배열
evaluation_functions = [
    evaluate_physical_health,
    evaluate_mental_health,
    evaluate_social_health,
    evaluate_lifestyle
]



@elder.route("/answer-daily-counseling", methods=['POST'])
@login_required
def answer_daily_counseling(current_user):
    """
    검사 답변을 토대로 점수를 계산하고 DB에 저장.
    """
    #! user.type에 맞는 점수 계산.
    answers = request.json['answers']
    elder = DB.Elder.query.filter_by(id=current_user.id).first()
    score = evaluation_functions[elder.counseling_type](answers)

    #! 점수 DB에 저장.
    new_score = DB.CounselingScore(elder_id=elder.id, 
                counseling_type=elder.counseling_type, score=score)
    
    db.session.add(new_score)
    db.session.commit()

    #! user.type ++.
    elder.update_counseling_type()

    return jsonify({'message': f'{score}'}), 200


@elder.route("/monthly-evaluation", methods=['POST'])
@login_required
def get_monthly_evaluation(current_user):
    """
    월별 평가를 저장하는 DB를 만들어.
    'monthly-evaluation' API가 호출되었을 때,
    해당월 점수가 계산이 안되어있으면 -> 해당 월 점수를 계산 후 반환
    해당월 점수가 계산이 되어있으면 -> 해당 월 점수 반환
    """
    #! 클라이언트에게 'YYYY-MM' 정보를 받는다.
    month = request.json['year_month']

    #! 해당 월의 월별평가가 존재하는지 검색
    monthly_evaluation = DB.MonthlyEvaluation.query.filter_by(elder_id=current_user.id, month=month).first()

    #! 월별평가가 존재하지 않으면 월별평가 계산
    if monthly_evaluation is None:
        scores = []
        for i in range(4):
            score = db.session.query(func.avg(DB.CounselingScore.score)).filter(
                DB.CounselingScore.counseling_type == i,
                text(f"DATE_FORMAT(date, '%Y-%m') = '{month}'")                 
            ).scalar()

            if score is not None:
                score = round(score, 1)
            scores.append(score)

        monthly_evaluation = DB.MonthlyEvaluation(current_user.id, month,
                                scores[0], scores[1], scores[2], scores[3])
        db.session.add(monthly_evaluation)
        db.session.commit()

    #! 월별평가 반환
    return jsonify({'month': f'{monthly_evaluation.month}',
                    'physical_score': f'{monthly_evaluation.physical_score}',
                    'mental_score': f'{monthly_evaluation.mental_score}',
                    'social_score': f'{monthly_evaluation.social_score}',
                    'lifestyle_score': f'{monthly_evaluation.lifestyle_score}',
                    }), 200 



@elder.route("/daily-question", methods=['GET'])
@login_required
def get_daily_question(current_user):
    """
    보호자가 등록한 질문을 반환하는 API
    """

    return jsonify({'message': f'ID: {current_user.id}'}), 200
