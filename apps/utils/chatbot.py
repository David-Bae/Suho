import time
import openai
from gtts import gTTS
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain import PromptTemplate


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}'s Latency: {end-start:.1f}(s)")

        return result
    return wrapper


def STT_legacy(audio):
    transcript = openai.Audio.transcribe("whisper-1", audio)
    return transcript["text"]

#! 경로 기반
def STT(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript


def GPT(question, user_answer):
    #! Language Model
    # chat = ChatOpenAI(model="gpt-3.5-turbo-0613") #! 말투가 띠꺼움.
    chat = ChatOpenAI(model="gpt-3.5-turbo-0125")
    # chat = ChatOpenAI(model="gpt-4")

    #! Prompt
    prompt = PromptTemplate(
        template="""
상담자가 다음과 같은 질문을 했습니다.
question: {question}
내담자(고령자)가 질문에 대해 다음과 같은 답변을 했습니다.
answer: {user_answer}
======================================================

내담자의 답변에 대해 깊이 공감하는 말을 2문장 이내의 한국어로 답변해주세요.
""",

        input_variables=["question", "user_answer"]
    )

    result = chat(
        [
            SystemMessage(content="당신은 고령자를 위한 상담사입니다. 존댓말을 쓰고 공감하는 말을 해주세요."),
            HumanMessage(content=prompt.format(question=question, user_answer=user_answer))
        ]
    )

    return result.content


def analysisGPT(elder_name, questions, user_answers, date):
    #! Language Model
    chat = ChatOpenAI(model="gpt-4-turbo-2024-04-09")

    QA = ""
    for i in range(len(user_answers)):
        QA += f"<{i+1}번째 질문 & 답변>\n"
        QA += f"Q: {questions[i]}\n"
        QA += f"A: {user_answers[i]}\n"
        QA += f"답변 날짜: {date[i]}\n\n"

    #! Prompt
    prompt = PromptTemplate(
        template="""
다음은 {elder_name}님의 생활 분석을 위한 상담 내역입니다. Q는 상담자가 질문한 내용이고, A는 {elder_name}님이 답변한 내용입니다.
======================================================
{QA} # QA에서 qa로 바꿈.
======================================================

위 답변을 토대로 {elder_name}님의 상태를 분석해서 {elder_name}님의 보호자에게 보여줄 보고서를 작성해주세요.
아래의 보고서 작성 지침을 지켜주세요.
1. 보고서는 2문단으로 작성해주세요.
2. 보고서의 첫번째 문단에는 보호자에게 {elder_name}님의 현재 상태를 분석하고 상황을 설명하는 내용을 작성해주세요.
3. 보고서의 두번째 문단에는 {elder_name}님을 위해서 보호자가 어떠한 조치를 취하면 좋을지 추천 또는 제안하세요.
4-1. '신체 건강' 또는 '정신 건강'을 분석한 결과 {elder_name}님의 상태가 건강하다면 보호자에게 건강한 상태를 알려주기만 하세요.
4-2. '신체 건강' 또는 '정신 건강'을 분석한 결과 {elder_name}님의 상태가 보통(가끔씩 아프지만 평소에는 괜찮음)이라면 보호자에게 {elder_name}님의 상태를 알려주면서 예방 & 주의를 해주세요.
4-3. '신체 건강' 또는 '정신 건강'을 분석한 결과 {elder_name}님의 상태가 좋지 않음(매일 아픔)이라면 보호자에게 {elder_name}님의 상태를 알려주면서 병원에서 진료를 받으라는 등 조치를 취하라고 경고하세요.
""",
        input_variables=["elder_name", "QA"]
    )

    result = chat(
        [
            SystemMessage(content="당신은 상담 내역을 토대로 보고서를 쓰는 사람입니다. 상담 대상은 고령자이고 보고서를 읽을 대상은 고령자의 보호자입니다."),
            HumanMessage(content=prompt.format(elder_name=elder_name, QA=QA))
        ]
    )

    return result.content


def TTS(text):
    tts = gTTS(text=text, lang="ko")
    return tts


def AudioChatbot(question, user_text):
    """
    question: 미리 지정된 질문 (str)
    user_audio: 고령자가 질문을 듣고 답한 음성 파일 (.mp3)
    STT, GPT, TTS를 거쳐 챗봇의 답변을 TTS로 생성하고 반환.
    tts는 mp3 파일이 아니다.
    """

    #! 질문과 고령자의 응답을 토대로 GPT 답변 생성.
    gpt_answer = GPT(question, user_text)
    print(f"GPT: {gpt_answer}") # 중간 결과물 출력.

    # #! GPT 답변을 음성파일로 변환.
    tts = TTS(gpt_answer)

    return tts

def get_audio_file_name(user_id, path):
    """
    현재는 user_id 와 생성시간으로 음성 파일 이름을 지정.
    추후에 user_id 와 user의 audio file 개수로 이름 지정할 것.
    Ex) 20190791_3.mp3 - 20190791 의 3번째 음성 파일.
    """
    current_time = datetime.now().strftime("%y%m%d%H%M%S")
    return f"{path}/{user_id}_{current_time}.mp3"

def is_mp3(filename: str) -> bool:
    return filename.endswith('.mp3')



"""
Legacy
"""
def SimpleGPT(user_input:str):
    chat = ChatOpenAI(model="gpt-3.5-turbo-0125")
    result = chat([HumanMessage(content=user_input)])

    return result.content

