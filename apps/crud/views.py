from flask import Blueprint, jsonify
from apps.auth.views import login_required

crud = Blueprint(
    "crud",
    __name__
)

@crud.route("/")
def index():
    return "Hello, CRUD!"

@crud.route("/test", methods=['POST'])
@login_required
def tell_my_name(current_user):
    return jsonify({'message': f'로그인한 사용자 이름은 {current_user.name}입니다.'})