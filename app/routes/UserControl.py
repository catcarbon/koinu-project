from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt

from app import db, blacklist
from app.Models import User

user_control = Blueprint('user_control', __name__)


@user_control.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'msg': 'Not json'}), 400

    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        return jsonify({'msg': 'Missing required fields'}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'msg': 'Username already registered'}), 400
    else:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        token = create_access_token(user.username)
        return jsonify({'user': user.username, 'msg': 'User creation successful', 'token': token}), 201


@user_control.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'msg': 'Not json'}), 400

    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        return jsonify({'msg': 'Missing required fields'}), 400

    user = User.query.filter_by(username=username, is_active=True).first()
    if user is None or not user.check_password(password):
        return jsonify({'message': 'Bad credentials'}), 401
    else:
        token = create_access_token(user.username)
        return jsonify({'username': user.username, 'msg': 'Login successful', 'access-token': token}), 200


@user_control.route('/logout')
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'logged out'}), 200
