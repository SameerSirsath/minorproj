from pymongo import MongoClient

# Connect to local MongoDB (no password, no username)
client = MongoClient('mongodb://localhost:27017/')
db = client['pwd_assistant']
users = db['users']

# Insert a test document
users.insert_one({'test': 'Hello MongoDB'})

# Read it back
doc = users.find_one({'test': 'Hello MongoDB'})
print("Success! Found:", doc)

# Clean up
users.delete_one({'test': 'Hello MongoDB'})
print("Test passed. MongoDB is ready.")