from apps.elder import elder_bp as elder
from apps.auth.views import login_required
from apps.crud import models as DB
from apps.app import db
from flask import request, jsonify, send_file
from sqlalchemy import func, text
import os
import json
from apps.utils import chatbot as chat
#from werkzeug.utils import secure_filename
from gtts import gTTS


#####################################################################################
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)

#! 정형화된 검사가 저장된 디렉토리(절대주소 사용)
COUNSELING_FILE_DIR = os.path.join(current_directory, 'questionnaires')
COUNSELING_NAME = ['0_physical_health', '1_mental_health', '2_social_health', '3_lifestyle']

#! 고령자 답변 음성 파일이 저장된 디렉토리(절대주소 사용)
ANSWER_AUDIO_DIR = os.path.join(current_directory, 'answer_audio')
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


#? AI 상담은 다수의 사용자가 동시에 요청할 수 있다.(제한 없음)
#? WebSocket을 사용하지 않고 캐시로 구현.
ID_CACHE = []
QUESTIONS_CACHE = {}

@elder.route("check-cache", methods=['GET'])
def check_cache():
    # ID_CACHE와 QUESTIONS_CACHE의 상태를 JSON 형식으로 반환
    return jsonify({
        "id_cache": ID_CACHE,
        "questions_cache": QUESTIONS_CACHE
    }), 200


@elder.route("/daily-question-isavailable", methods=['POST'])
@login_required
def daily_question_isavailable(current_user):
    """_summary_
    'daily-question' API를 호출하기 전에 질문이 남아있는지 확인하는 API
    
    Args:
        current_user : elder_id

    Returns:
        int: 1=질문O, 0=질문X
    """
    
    global ID_CACHE
    global QUESTIONS_CACHE

    elder_id = current_user.id
    
    if elder_id in ID_CACHE:
        #! 이전에 한번 호출해서 Cache에 고령자 ID가 남아 있는 경우.
        if QUESTIONS_CACHE[elder_id]:
            return jsonify({'message': 1}), 200
        else:
            ID_CACHE.remove(elder_id)
            del QUESTIONS_CACHE[elder_id]
            return jsonify({'message': 0}), 200
    else:
        ID_CACHE.append(elder_id)
        QUESTIONS_CACHE[elder_id] = []
        
        #! DB에서 질문 가져오기
        questions_DB = db.session.query(DB.CustomQuestion.question).filter_by(elder_id=elder_id).all()
        if not questions_DB:
            ID_CACHE.remove(elder_id)
            del QUESTIONS_CACHE[elder_id]
            return jsonify({'message': 0}), 200

        for question in questions_DB:
            QUESTIONS_CACHE[elder_id].append(str(question[0]))

        return jsonify({'message': 1}), 200
    
    

@elder.route("/daily-question", methods=['POST'])
@login_required
def get_daily_question(current_user):
    """
    보호자가 등록한 질문을 반환하는 API
    """
    global ID_CACHE
    global QUESTIONS_CACHE

    elder_id = current_user.id

    #! 질문을 TTS로 변환하여 클라이언트에 전달
    tts = gTTS(text=QUESTIONS_CACHE[elder_id][0], lang='ko')
    tts_file_path = os.path.join(os.getcwd(), f'temp/{elder_id}_response.mp3')
    tts.save(tts_file_path)
    
    return send_file(tts_file_path, as_attachment=True, download_name=f"{elder_id}_response.mp3", mimetype="audio/mpeg")


#? MP3 File Format Checker
ALLOWED_EXTENSIONS = {'mp3', 'm4a'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@elder.route("/answer-daily-question", methods=['POST'])
@login_required
def answer_daily_question(current_user):
    """
    질문에 대한 고령자 음성 답변을 등록하는 API
    """
    elder_id = current_user.id

    #? 클라이언트로부터 mp3 받기
    if 'file' not in request.files:
        return jsonify({'error': 'request에 파일이 없습니다.'}), 400

    #! file = 클라이언트가 업로드한 file object.
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'mp3 파일이 없습니다.'}), 400


    #! 여기서부터 mp3 파일이 있는 경우.
    #! 1. question으로 QuestionAnswer 객체 생성
    qa = DB.QuestionAnswer(elder_id=elder_id, question=QUESTIONS_CACHE[elder_id][0])
    
    if file and allowed_file(file.filename):
        #! 2. SER에 입력될 mp3 파일 이름을 QuestionAnswer의 id로 저장
        _, format = file.filename.split('.')
        filename = f"{qa.id}.{format}"
        file_path = os.path.join(ANSWER_AUDIO_DIR, filename)
        file.save(file_path)

        #! 3. STT & QuestionAnswer 객체에 사용자 답변 text 저장
        answer_text = chat.STT(file_path)
        
        qa.answer = answer_text
        db.session.add(qa)
        db.session.commit()
        
        #! 4. GPT 답변 TTS 생성 후 반환 & 질문 삭제
        gpt_tts = chat.AudioChatbot(QUESTIONS_CACHE[elder_id][0], answer_text)        
        tts_file_path = os.path.join(os.getcwd(), f'temp/{elder_id}_response.mp3')
        gpt_tts.save(tts_file_path)
        
        del QUESTIONS_CACHE[elder_id][0]

        return send_file(tts_file_path, as_attachment=True, download_name=f"{elder_id}_response.mp3", mimetype="audio/mpeg")

    if not file:
        return jsonify({'error': 'File 없음'}), 400
    else:
        return jsonify({'error': 'File type not allowed'}), 400
