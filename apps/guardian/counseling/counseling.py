from apps.guardian import guardian_bp as guardian
from apps.auth.views import login_required
from flask import request, jsonify
from apps.crud import models as DB
from apps.app import db
from datetime import date
from sqlalchemy import and_
from apps.utils import chatbot as chat

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

month_end_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
def get_date_range(month_str):
    year, month = map(int, month_str.split('-'))
    
    # 윤년 계산 (2월이 29일이 되는 경우)
    if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
        end_day = 29
    else:
        end_day = month_end_days[month - 1]
    
    start_date = date(year, month, 1)
    end_date = date(year, month, end_day)
    
    return start_date, end_date

@guardian.route('/monthly-analysis', methods=['POST'])
def monthly_analysis():
    elder_id = request.json['elder_id']
    month = request.json['month']

    elder_name = db.session.query(DB.Elder.name).filter(DB.Elder.id == elder_id).scalar()

    start_date, end_date = get_date_range(month)

    results = db.session.query(DB.QuestionAnswer).filter(
        and_(
            DB.QuestionAnswer.elder_id == elder_id,
            DB.QuestionAnswer.date >= start_date,
            DB.QuestionAnswer.date <= end_date
        )
    ).order_by(DB.QuestionAnswer.date.asc()).all()

    questions = []
    answers = []
    qa_date = []

    for qa in results:
        questions.append(qa.question)
        answers.append(qa.answer)
        qa_date.append(qa.date)

    gpt_analysis = chat.analysisGPT(elder_name, questions, answers, qa_date)

    return jsonify({'result': gpt_analysis}), 200