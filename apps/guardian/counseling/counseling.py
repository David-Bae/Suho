from apps.guardian import guardian_bp as guardian
from apps.auth.views import login_required
from flask import request, jsonify
from apps.crud import models as DB
from apps.app import db
from datetime import date
from sqlalchemy import and_
from apps.utils import chatbot as chat
from apps.utils import utils
from apps.utils import report_maker as rp

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
@guardian.route("/counseling/make-report", methods=['POST'])
@login_required
def make_report(current_user):
    elder_id = request.json['elder_id']
    elder_name = DB.Elder.query.filter(DB.Elder.id == elder_id).first().name
    year = request.json['year']
    month = request.json['month']
    year_month = utils.format_year_month(year, month)
    
    #! GPT 분석 (병렬1)
    # start_date, end_date = utils.get_date_range(year_month)

    # results = db.session.query(DB.QuestionAnswer).filter(
    #     and_(
    #         DB.QuestionAnswer.elder_id == elder_id,
    #         DB.QuestionAnswer.date >= start_date,
    #         DB.QuestionAnswer.date <= end_date
    #     )
    # ).order_by(DB.QuestionAnswer.date.asc()).all()

    # questions = []
    # answers = []
    # qa_date = []

    # for qa in results:
    #     questions.append(qa.question)
    #     answers.append(qa.answer)
    #     qa_date.append(qa.date)

    # gpt_analysis = chat.analysisGPT(elder_name, questions, answers, qa_date)
    
    
    #! 정형화된 검사 (병렬2)
    
    
    
    #! 보고서 만들기 (PDF & PNG)
    filename = f'{elder_id}_{year_month}'
    args = [elder_name, year_month, 0, [88,11,55,33], ["아르테타", "벵거"], filename]
    
    rp.draw(*args)
    rp.pdf2img(filename)
    
    
    #! 보고서 반환 (PNG)
    return jsonify({"message": "Done."})
    
















@guardian.route("make-report", methods=['POST'])
def make__report():
    name = request.json['name']
    month = request.json['month']
    filename = 1234
    args = [name, month, 0, [100,60,100,30], [test_text1, test_text2], filename]
    
    rp.draw(*args)
    rp.pdf2img(filename)
    
    
    
    return jsonify({"message": "done"}), 200































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

@guardian.route("/monthly-evaluation", methods=['POST'])
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