from flask import Blueprint, request, jsonify
from apps.crud import models as DB
from datetime import date, datetime, timedelta

elder = Blueprint(
    "elder",
    __name__
)

@elder.route("/")
def index():
    return "Hello, elder!"