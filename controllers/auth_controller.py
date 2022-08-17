from flask import Blueprint, request, abort, jsonify
from main import db
from schemas.user_schema import user_schema, users_schema
from models.users import User
from main import bcrypt
from datetime import timedelta
from flask_jwt_extended import create_access_token


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route('/register', methods=["POST"])
def auth_register():
    user_fields = user_schema.load(request.json)
    user = User.query.filter_by(username=user_fields["username"]).first()
    if user:
        return abort(401, description="Username already exists")
    else:
        user = User()
        user.username = user_fields["username"]
        user.password = bcrypt.generate_password_hash(user_fields["password"]).decode("utf-8")
        user.admin = False

        db.session.add(user)
        db.session.commit()

        expiry = timedelta(days=1)
        access_token = create_access_token(identity=str(user.id), expires_delta=expiry)

        return jsonify({"user": user.username, "token": access_token})


@auth.route('/login', methods=["POST"])
def auth_login():
    user_fields = user_schema.load(request.json)
    user = User.query.filter_by(username=user_fields["username"]).first()
    if not user or not bcrypt.check_password_hash(user.password, user_fields["password"]):
        return abort(401, description="Invalid login")
    
    expiry = timedelta(days=1)
    access_token = create_access_token(identity=str(user.id),expires_delta=expiry)

    return jsonify({"user": user.username, "token": access_token})
