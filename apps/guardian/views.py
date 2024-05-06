from flask import Blueprint, request, jsonify
from apps.crud import models as DB
from datetime import date, datetime, timedelta

guardian = Blueprint(
    "guardian",
    __name__
)

@guardian.route("/")
def index():
    return "Hello, Guardian!"