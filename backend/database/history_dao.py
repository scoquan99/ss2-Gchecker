from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from datetime import datetime
from config import MONGO_URI, DB_NAME

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    history_collection = db["history"]
    try:
        history_collection.create_index(
            [("username", ASCENDING), ("created_at", DESCENDING)],
            name="hist_user_created"
        )
    except Exception:
        pass   # index đã tồn tại
except PyMongoError as e:
    import sys
    print(f"[FATAL] Cannot connect to MongoDB: {e}", file=sys.stderr)
    history_collection = None


def save_history(text, result, lang="en-US", username=None):
    # DB-2 fix: chỉ lưu summary nhỏ gọn, không lưu toàn bộ blob
    summary = result.get("summary", {}) if isinstance(result, dict) else {}
    data = {
        "text":       text[:2000],   # giới hạn text lưu
        "lang":       lang,
        "username":   username,
        "result": {
            "summary":        summary,
            "corrected_text": (result.get("corrected_text") or "")[:2000],
        },
        "created_at": datetime.utcnow()
    }
    try:
        history_collection.insert_one(data)
    except PyMongoError as e:
        print(f"[history_dao] save error: {e}")


def get_history(limit=20, username=None):
    query = {}
    if username:
        query["username"] = username
    try:
        history = list(
            history_collection
            .find(query)
            .sort("created_at", -1)
            .limit(limit)
        )
        for item in history:
            item["_id"] = str(item["_id"])
        return history
    except PyMongoError as e:
        print(f"[history_dao] get error: {e}")
        return []


def delete_history_item(item_id, username=None):
    from bson import ObjectId
    try:
        query = {"_id": ObjectId(item_id)}
        if username:
            query["username"] = username
        result = history_collection.delete_one(query)
        return result.deleted_count > 0
    except Exception:
        return False


def delete_all_history(username=None):
    query = {}
    if username:
        query["username"] = username
    try:
        result = history_collection.delete_many(query)
        return result.deleted_count
    except PyMongoError:
        return 0
