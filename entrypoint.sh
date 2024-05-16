#!/bin/bash
# 데이터베이스 마이그레이션 실행
flask db migrate
flask db upgrade

# 애플리케이션 시작
flask run --host=0.0.0.0