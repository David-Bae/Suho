import phonenumbers
from zoneinfo import ZoneInfo
from datetime import datetime
import bcrypt
from sdk.api.message import Message
from apps.config import COOLSMS_KEY, COOLSMS_SECRET
import string, random
from apps.crud import models as DB
from apps.app import db
from datetime import date, datetime, timedelta


# 전화 번호 형식 검증 함수.
def validate_phone_number(phone_number):
    try:
        number = phonenumbers.parse(phone_number, "KR")
        return phonenumbers.is_valid_number(number)
    except phonenumbers.NumberParseException:
        return False


# 비밀번호를 암호화(해싱)하는 함수.
def hashing_password(password):
    password_bytes = password.encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hash.decode()

def check_password(password, db_password):
    password = hashing_password(password)
    db_password = db_password.encode('utf-8')
    return bcrypt.checkpw(password, db_password)


# 회원가입시 인증 코드를 보내는 함수.
def send_verification_sms(phone, code):
    params = dict()
    params['type'] = 'sms' 
    params['to'] = phone
    params['from'] = '01024252309' #! 고정.
    params['text'] = f"[수호] 인증번호 [{code}] *타인에게 절대 알리지 마세요."

    cool = Message(COOLSMS_KEY, COOLSMS_SECRET)
    cool.send(params)

# 고령자-보호자 계정 연동에 필요한 연동 코드 생성
def create_connection_code():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(15))
    return code

# 서울의 현재 시간 반환
def get_current_time_seoul():
    now = datetime.now(tz=ZoneInfo('UTC'))
    now = now.astimezone(ZoneInfo('Asia/Seoul'))

    return now

# 해당월의 시작날과 마지막날을 반환.
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

# year, month 를 "YYYY-MM" 형식으로 변환.
def format_year_month(year, month):
    year = str(year)
    month = str(month)
    
    if len(month) == 1:
        month = '0' + month
    
    return f"{year}-{month}"
