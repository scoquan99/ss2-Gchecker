from flask import Blueprint, request, jsonify
import jwt, datetime, os
from database.user_model import create_user, find_user, verify_password
from pymongo.errors import DuplicateKeyError

auth_routes = Blueprint("auth_routes", __name__)
SECRET_KEY = os.environ.get("JWT_SECRET", "your-secret-key")

@auth_routes.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    try:
        create_user(username, password)
        return jsonify({"message": "Registered successfully"}), 201
    except DuplicateKeyError:
        return jsonify({"error": "Username already exists"}), 400


@auth_routes.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = find_user(username)
    if not user or not verify_password(password, user["password"]):
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token, "preferred_language": user.get("preferred_language", "en-US")})