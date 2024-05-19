from flask import Blueprint

guardian_bp = Blueprint(
    "guardian",
    __name__
)

from . import views