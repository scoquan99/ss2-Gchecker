from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
history_collection = db["history"]


def save_history(text, result, lang="en-US", username=None):
    data = {
        "text":       text,
        "result":     result,
        "lang":       lang,
        "username":   username,   # ← lưu username để filter
        "created_at": datetime.utcnow()
    }
    history_collection.insert_one(data)


def get_history(limit=20, username=None):
    query = {}
    if username:
        query["username"] = username   # ← mỗi user chỉ thấy history của mình

    history = list(
        history_collection
        .find(query)
        .sort("created_at", -1)
        .limit(limit)
    )
    for item in history:
        item["_id"] = str(item["_id"])
    return history