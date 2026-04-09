import bcrypt
from datetime import datetime

# Simple in-memory storage for development (replace with MongoDB later)
users_db = {}

def create_user(username, password, email=None, full_name=None):
    if username in users_db:
        raise Exception("Username already exists")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users_db[username] = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": hashed,
        "created_at": datetime.utcnow()
    }

def find_user(username):
    return users_db.get(username)

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed)
