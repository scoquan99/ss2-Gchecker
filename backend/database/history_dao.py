from datetime import datetime

# Simple in-memory storage for development (replace with MongoDB later)
history_db = []


def save_history(text, result):
    """
    Lưu lịch sử kiểm tra grammar vào memory
    """
    data = {
        "text": text,
        "result": result,
        "created_at": datetime.utcnow(),
        "_id": str(len(history_db))  # Simple ID
    }
    history_db.append(data)


def get_history(limit=10):
    """
    Lấy lịch sử kiểm tra gần nhất
    """
    return history_db[-limit:][::-1]  # Get last N items, reverse to show newest first