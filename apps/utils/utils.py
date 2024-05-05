import phonenumbers

# 전화 번호 형식 검증 함수.
def validate_phone_number(phone_number):
    try:
        number = phonenumbers.parse(phone_number, "KR")
        return phonenumbers.is_valid_number(number)
    except phonenumbers.NumberParseException:
        return False

import bcrypt

# 비밀번호를 암호화(해싱)하는 함수.
def hashing_password(password):
    password_bytes = password.encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hash #.decode('utf-8')