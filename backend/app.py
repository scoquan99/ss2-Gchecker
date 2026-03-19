from flask import Flask
from flask_cors import CORS
from routes.check_routes import check_routes

app = Flask(__name__)

CORS(app)

app.register_blueprint(check_routes)

if __name__ == "__main__":

    app.run(debug=True)