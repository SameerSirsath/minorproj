# import bcrypt
# password = "test123"
# hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
# print(hashed)

from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["pwd_assistant"]
user = db.users.find_one({"username": "your_ngo_username"})
print(user.get("user_type"))