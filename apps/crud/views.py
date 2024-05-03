from flask import Blueprint, render_template

crud = Blueprint(
    "crud",
    __name__
)

@crud.route("/")
def index():
    return "Hello, CRUD!"