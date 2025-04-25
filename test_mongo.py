# test_mongo.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Replace with your actual connection string from MongoDB Atlas
CONNECTION_STRING = (
    "mongodb+srv://ben:ben123@Cluster0.mongodb.net/?retryWrites=true&w=majority"
)


async def test_connection():
    try:
        client = AsyncIOMotorClient(CONNECTION_STRING)
        # Force a connection to verify it works
        await client.admin.command("ping")
        print("✅ Connected to MongoDB successfully!")
        client.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(
            f"Please check your connection string and ensure your IP is whitelisted in MongoDB Atlas."
        )


# Run the test
if __name__ == "__main__":
    asyncio.run(test_connection())
