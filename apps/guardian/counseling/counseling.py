from apps.guardian import guardian_bp as guardian
from apps.auth.views import login_required
from flask import request, jsonify, send_file
from apps.crud import models as DB
from apps.app import db
from datetime import date
from sqlalchemy import and_
from apps.utils import chatbot as chat
from apps.utils import utils
from apps.utils import report_maker as rp
from sqlalchemy import func, extract
import os

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


#! Suho 앱의 핵심. (SER 제외 구현)
@guardian.route("/counseling/make-report/<elder_id>/<year>/<month>", methods=['POST'])
@login_required
def get_report(current_user, elder_id, year, month):
    year_month = utils.format_year_month(year, month)

    #! 보고서 파일이 이미 존재하면 바로 반환.
    report_filename = f'{elder_id}_{year_month}'
    image_path = os.path.join(rp.REPORT_DIR, f'{report_filename}.png')
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png'), 200
    
    #! GPT 분석
    start_date, end_date = utils.get_date_range(year_month)

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

    elder_name = DB.Elder.query.filter(DB.Elder.id == elder_id).first().name
    current_status_analysis, care_recommendations = chat.analysisGPT(elder_name, questions, answers, qa_date)

    #! 정형화된 검사
    scores = []
    for i in range(4):
        avg_score = db.session.query(func.avg(DB.CounselingScore.score)).filter(
            DB.CounselingScore.elder_id == elder_id,
            DB.CounselingScore.counseling_type == i,
            extract('year', DB.CounselingScore.date) == year,
            extract('month', DB.CounselingScore.date) == month
        ).scalar()

        scores.append(round(avg_score))

    #! 보고서 만들기 (PDF & PNG)
    args = [elder_name, year_month, 0, scores, [current_status_analysis, care_recommendations], report_filename]

    rp.draw(*args)
    image_path = rp.pdf2img(report_filename)

    #! 보고서 반환 (PNG)
    try:
        return send_file(image_path, mimetype='image/png'), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500