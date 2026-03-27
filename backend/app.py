from flask import Flask
from flask_cors import CORS
from routes.check_routes import check_routes
from routes.auth_routes import auth_routes

app = Flask(__name__)

CORS(app, origins=["*"], supports_credentials=True)

app.register_blueprint(check_routes)
app.register_blueprint(auth_routes)

if __name__ == "__main__":

    app.run(debug=True)