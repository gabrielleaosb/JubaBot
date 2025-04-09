from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

client = None
db = None

async def connect_to_db():
    global client, db
    mongo_url = os.getenv("MONGO_URL")
    client = AsyncIOMotorClient(mongo_url)
    db = client["bot_database"]  
    print("🟢 Conectado ao MongoDB")

def get_db():
    return db
