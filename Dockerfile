# Python 이미지 사용
FROM python:3.11.4

# 작업 디렉토리 설정
WORKDIR /usr/src/

# 시스템 패키지 업데이트 및 poppler-utils 설치
RUN apt-get update && apt-get install -y poppler-utils

# 의존성 파일 복사
COPY ./requirements.txt /usr/src/requirements.txt

# pip의 version 갱신
RUN pip install --upgrade pip

# Python 라이브러리 설치
RUN pip install -r requirements.txt

# 애플리케이션 실행
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
