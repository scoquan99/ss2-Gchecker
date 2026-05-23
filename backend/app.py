from flask import Flask
from flask_cors import CORS
from routes.check_routes import check_routes
from routes.auth_routes import auth_routes
from routes.chat_routes import chat_routes
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
app.register_blueprint(chat_routes)

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port  = int(os.getenv("PORT", 5000))
    print(f"Server running on http://localhost:{port} (debug={debug})")
    app.run(debug=debug, port=port)

@app.errorhandler(Exception)
def _json_500(e):
    app.logger.exception(e)
    return jsonify({"error": "Internal server error"}), 500