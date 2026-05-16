from flask import Flask
from flask_cors import CORS
from routes.check_routes import check_routes
from routes.auth_routes import auth_routes
from dotenv import load_dotenv
import os
import nltk_download

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)

# ================== CORS FIX ==================
CORS(app, 
     origins=["http://localhost:8000", "http://127.0.0.1:8000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     supports_credentials=True,
     max_age=3600)   # Cache preflight 1 giờ

# Hoặc cách mạnh hơn (nếu vẫn lỗi):
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)
# ===============================================

app.register_blueprint(check_routes)
app.register_blueprint(auth_routes)

if __name__ == "__main__":
    print("🚀 Server running on http://localhost:5000")
    app.run(debug=True, port=5000)