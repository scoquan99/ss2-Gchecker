import bcrypt
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_col = db["users"]

# Đảm bảo username là duy nhất
users_col.create_index("username", unique=True)


def create_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users_col.insert_one({
        "username": username,
        "password": hashed,
        "created_at": datetime.utcnow()
    })


def find_user(username):
    return users_col.find_one({"username": username})


def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed)

def save_preferred_language(username, lang):
    users_col.update_one({"username": username}, {"$set": {"preferred_language": lang}})

def get_preferred_language(username):
    user = find_user(username)
    return user.get("preferred_language", "en-US") if user else "en-US"