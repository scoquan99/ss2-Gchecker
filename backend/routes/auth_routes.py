from flask import Blueprint, request, jsonify
import jwt, datetime, os
from database.user_model import create_user, find_user, verify_password
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")
auth_routes = Blueprint("auth_routes", __name__)

import re

@auth_routes.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email = data.get("email", "").strip()
    full_name = data.get("full_name", "").strip()

    # Username validation
    if " " in username:
        return jsonify({"error": "Username cannot contain spaces or special characters."}), 400
    username = username.strip()
    if not (5 <= len(username) <= 30):
        return jsonify({"error": "Username must be between 5 and 30 characters long."}), 400
    if not re.match(r"^[a-zA-Z0-9_.]+$", username):
        return jsonify({"error": "Username cannot contain spaces or special characters."}), 400

    # Password validation
    if not password:
        return jsonify({"error": "Password is required."}), 400
    password = password.strip()
    if not (8 <= len(password) <= 128):
        return jsonify({"error": "Password must be between 8 and 128 characters long."}), 400
    if not any(c.isupper() for c in password):
        return jsonify({"error": "Password must contain at least one uppercase letter."}), 400
    if not any(c.islower() for c in password):
        return jsonify({"error": "Password must contain at least one lowercase letter."}), 400
    if not any(c.isdigit() for c in password):
        return jsonify({"error": "Password must contain at least one number."}), 400
    if not re.search(r"[@$!%*?&#^()_+=\-{}\[\]|\\:;\"'<>,./~`]", password):
        return jsonify({"error": "Please include at least one special character (e.g., @, #, $)."}), 400

    # Email validation
    if not (6 <= len(email) <= 255):
        return jsonify({"error": "Email must be between 6 and 255 characters long."}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format."}), 400

    # Full Name validation
    if not (2 <= len(full_name) <= 100):
        return jsonify({"error": "Full Name must be between 2 and 100 characters long."}), 400

    try:
        create_user(username, password, email=email, full_name=full_name)
        return jsonify({"message": "Registered successfully"}), 201
    except Exception as e:
        if "already exists" in str(e):
            return jsonify({"error": "Username already exists"}), 400
        return jsonify({"error": "Registration failed"}), 500


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

    return jsonify({
        "token": token,
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "email": user.get("email", "")
    })