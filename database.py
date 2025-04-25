from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
import os
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception:
    pass  # Continue even if .env file doesn't exist

# Get MongoDB connection string from environment variable or use your direct string
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "filmtrack_db")

client = None
db = None


async def connect_to_mongo():
    """Connect to MongoDB and initialize collections with indexes"""
    global client, db

    try:
        # Connect to MongoDB
        print(f"Attempting to connect to MongoDB at: {MONGODB_URL}")
        client = AsyncIOMotorClient(MONGODB_URL)

        # Test connection with ping
        await client.admin.command("ping")
        print("MongoDB connection successful!")

        db = client[DB_NAME]

        # Create indexes for movies collection
        await db.movies.create_index([("user_id", ASCENDING)])

        # Create indexes for users collection
        await db.users.create_index([("username", ASCENDING)], unique=True)
        await db.users.create_index([("email", ASCENDING)], unique=True)

        print(f"✅ Connected to MongoDB, database: {DB_NAME}")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("❌ MongoDB connection closed")


def get_db():
    """Return database instance"""
    return db
