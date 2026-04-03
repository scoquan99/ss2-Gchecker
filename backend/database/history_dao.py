from pymongo import MongoClient
from datetime import datetime

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client["grammar_checker"]

history_collection = db["history"]


def save_history(text, result, lang="en-US"):
    """
    Lưu lịch sử kiểm tra grammar vào MongoDB
    """

    data = {
        "text": text,
        "result": result,
        "lang": lang,
        "created_at": datetime.utcnow()
    }

    history_collection.insert_one(data)


def get_history(limit=10):
    """
    Lấy lịch sử kiểm tra gần nhất
    """

    history = list(
        history_collection
        .find()
        .sort("created_at", -1)
        .limit(limit)
    )

    for item in history:
        item["_id"] = str(item["_id"])

    return history