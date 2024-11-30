from pymongo import MongoClient

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "news_database"
COLLECTION_NAME = "indian_express_articles"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Retrieve all documents
all_articles = collection.find()
print("All Articles:")
for article in all_articles:
    print(article)

# Retrieve documents with a filter
filtered_articles = collection.find({"title": {"$regex": "India"}})  # Search titles containing 'India'
print("\nFiltered Articles:")
for article in filtered_articles:
    print(article)

# Count documents
total_count = collection.count_documents({})
print(f"\nTotal Articles: {total_count}")
