# Python 이미지 사용
FROM python:3.9.19

# 작업 디렉토리 설정
WORKDIR /usr/src/

# 의존성 파일 복사
COPY ./requirements.txt /usr/src/requirements.txt

# pip의 version 갱신
RUN pip install --upgrade pip

# Python 라이브러리 설치
RUN pip install -r requirements.txt

# 애플리케이션 실행
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
