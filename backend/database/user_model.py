import bcrypt
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_col = db["users"]

users_col.create_index("username", unique=True)


def create_user(username, password, email=None, full_name=None):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        users_col.insert_one({
            "username":   username,
            "email":      email,
            "full_name":  full_name,
            "password":   hashed,
            "created_at": datetime.utcnow()
        })
    except DuplicateKeyError:
        raise Exception("Username already exists")


def find_user(username):
    return users_col.find_one({"username": username})


def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed)


def save_preferred_lang(username, lang):
    users_col.update_one(
        {"username": username},
        {"$set": {"preferred_lang": lang}}
    )


def get_preferred_lang(username):
    user = find_user(username)
    return user.get("preferred_lang", "en-US") if user else "en-US"