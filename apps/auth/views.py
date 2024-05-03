from flask import Blueprint, render_template, request, jsonify

auth = Blueprint(
    "auth",
    __name__
)

users = {}



@auth.route("/")
def index():
    return "Hello, Auth!"

@auth.route("/sign-up", methods=['POST'])
def sign_up():
    new_user            = request.json
    new_user["id"]      = 20190791
    users[20190791]     = new_user

    return jsonify(new_user)

@auth.route("/users", methods=['GET'])
def get_users():
    return jsonify(users[20190791])