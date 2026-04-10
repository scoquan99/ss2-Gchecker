from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, DB_NAME  # ← dùng config thay vì hardcode

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
history_collection = db["history"]


def save_history(text, result, lang="en-US"):  # ← thêm lang
    data = {
        "text":       text,
        "result":     result,
        "lang":       lang,  # ← thêm
        "created_at": datetime.utcnow()
    }
    history_collection.insert_one(data)


def get_history(limit=10):
    history = list(
        history_collection
        .find()
        .sort("created_at", -1)
        .limit(limit)
    )
    for item in history:
        item["_id"] = str(item["_id"])
    return history