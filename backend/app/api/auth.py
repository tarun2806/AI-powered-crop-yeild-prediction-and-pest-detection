from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, User
from ..schemas import UserSchema
from marshmallow import ValidationError

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        validated_data = user_schema.load(data)
        
        if User.query.filter_by(email=validated_data.email).first():
            return jsonify({"error": "Email already exists"}), 400
            
        hashed_pw = generate_password_hash(data['password'])
        new_user = User(
            email=validated_data.email,
            password_hash=hashed_pw,
            full_name=data.get('full_name')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User registered successfully"}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
        
    return jsonify({"error": "Invalid credentials"}), 401
