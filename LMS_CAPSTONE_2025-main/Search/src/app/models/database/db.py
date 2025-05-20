from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="./app/config/.env")

# MongoDB Connection (pymongo)
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://lmscapstone38:lmscapstone2025@lmscluster.i9xar.mongodb.net/?retryWrites=true&w=majority&appName=LMSCluster")
client = MongoClient(MONGO_URL)
db = client["sample_mflix"]

def get_db():
    return db

def close_db():
    client.close()