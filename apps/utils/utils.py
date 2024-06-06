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

# 고령자-보호자 계정에서 약 추가
def add_medicine(elder_id, title, start_year, start_month, start_day,
                 end_year, end_month, end_day, medicine_period, memo,
                 do_alarm, confirm_alarm_minute):

    new_medicine = DB.Medicine(title=title, elder_id=elder_id, start_year=start_year,
                               start_month=start_month, start_day=start_day, end_year=end_year,
                               end_month=end_month, end_day=end_day, medicine_period=medicine_period,
                               memo=memo, do_alarm=do_alarm, confirm_alarm_minute=confirm_alarm_minute)

    db.session.add(new_medicine)
    db.session.commit()

    period_times = {
        0: [(8, 0)],  # 일어나서 1회 (8:00 AM)
        1: [(22, 0)],  # 자기전 1회 (10:00 PM)
        2: [(8, 0), (20, 0)],  # 아침저녁 (8:00 AM, 8:00 PM)
        3: [(8, 0), (12, 0), (18, 0)],  # 아침점심저녁 (8:00 AM, 12:00 PM, 6:00 PM)
        4: [(8, 0)]  # 기타 (default to 8:00 AM)
    }

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    current_date = start_date

    alarm_times = period_times[medicine_period]

    while current_date <= end_date:
        for time in alarm_times:
            hour, minute = time
            medicine_time = datetime(current_date.year, current_date.month, current_date.day, hour, minute)
            alarm_time = medicine_time - timedelta(minutes=do_alarm)
            new_alarm = DB.MedicineAlarm(
                medicine_id=new_medicine.id,
                elder_id=elder_id,
                year=alarm_time.year,
                month=alarm_time.month,
                day=alarm_time.day,
                hour=alarm_time.hour,
                minute=alarm_time.minute,
                do_alarm=True,
                confirm_alarm_minute=confirm_alarm_minute
            )
            db.session.add(new_alarm)
        current_date += timedelta(days=1)

    db.session.commit()