# 전화 번호 형식 검증 함수.
import phonenumbers

def validate_phone_number(phone_number):
    try:
        number = phonenumbers.parse(phone_number, "KR")
        return phonenumbers.is_valid_number(number)
    except phonenumbers.NumberParseException:
        return False


# 비밀번호를 암호화(해싱)하는 함수.
import bcrypt

def hashing_password(password):
    password_bytes = password.encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hash #.decode('utf-8')


# 회원가입시 인증 코드를 보내는 함수.
from sdk.api.message import Message
from apps.config import COOLSMS_KEY, COOLSMS_SECRET

def send_verification_sms(phone, code):
    params = dict()
    params['type'] = 'sms' 
    params['to'] = phone
    params['from'] = '01024252309' #! 고정.
    params['text'] = f"[수호] 인증번호 [{code}] *타인에게 절대 알리지 마세요."

    cool = Message(COOLSMS_KEY, COOLSMS_SECRET)
    cool.send(params)