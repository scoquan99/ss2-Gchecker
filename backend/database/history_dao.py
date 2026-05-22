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
        "username":   username,   # luu username de filter
        "created_at": datetime.utcnow()
    }
    history_collection.insert_one(data)


def get_history(limit=20, username=None):
    query = {}
    if username:
        query["username"] = username   # moi user chi thay history cua minh

    history = list(
        history_collection
        .find(query)
        .sort("created_at", -1)
        .limit(limit)
    )
    for item in history:
        item["_id"] = str(item["_id"])
    return history


def delete_history_item(item_id, username=None):
    """Xoa mot muc lich su theo _id, chi xoa neu thuoc ve username."""
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
    """Xoa toan bo lich su cua mot user."""
    query = {}
    if username:
        query["username"] = username
    result = history_collection.delete_many(query)
    return result.deleted_count
