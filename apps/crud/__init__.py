import apps.crud.models
from flask import Blueprint

crud_bp = Blueprint(
    "crud",
    __name__
)

# 해당 Blueprint에 포함된 패키지들을 포함
from . import views