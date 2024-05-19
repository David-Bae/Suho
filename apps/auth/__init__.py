from flask import Blueprint

auth_bp = Blueprint(
    "auth",
    __name__
)

# 해당 Blueprint에 포함된 패키지들을 포함
from . import views