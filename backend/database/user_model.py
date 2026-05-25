import bcrypt
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime
from config import MONGO_URI, DB_NAME

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")   # fail fast nếu Mongo down
    db = client[DB_NAME]
    users_col = db["users"]
    try:
        users_col.create_index("username", unique=True, name="uniq_username")
    except Exception:
        pass   # index đã tồn tại với tên khác — không sao
except PyMongoError as e:
    import sys
    print(f"[FATAL] Cannot connect to MongoDB: {e}", file=sys.stderr)
    # Không crash cả app, nhưng mọi query sẽ raise lỗi rõ ràng
    client = None
    db = None
    users_col = None


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
    except PyMongoError as e:
        raise Exception(f"Database error: {e}")


def find_user(username):
    try:
        return users_col.find_one({"username": username})
    except PyMongoError:
        return None


def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed)


def save_preferred_lang(username, lang):
    try:
        users_col.update_one(
            {"username": username},
            {"$set": {"preferred_lang": lang}}
        )
    except PyMongoError:
        pass


def get_preferred_lang(username):
    user = find_user(username)
    return user.get("preferred_lang", "en-US") if user else "en-US"
