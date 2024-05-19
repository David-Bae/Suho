from flask import Blueprint

elder_bp = Blueprint(
    "elder",
    __name__
)

# 해당 Blueprint에 포함된 패키지들을 포함
from . import views
from . import counseling
