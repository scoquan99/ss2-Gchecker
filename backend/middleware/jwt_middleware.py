from functools import wraps
from flask import request, jsonify, g
import jwt, os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth.split(" ")[1]

        # Từ chối sentinel "guest" rõ ràng
        if token == "guest":
            return jsonify({"error": "Please log in"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Please log in"}), 401

        # Gắn username vào g — handlers dùng g.username, không decode lại
        username = payload.get("username")
        if not username:
            return jsonify({"error": "Invalid token"}), 401

        g.username = username
        return f(*args, **kwargs)
    return decorated
