import os
from mongoengine import connect as mongoengine_connect_db
from pymongo import MongoClient
from pymongo.collection import Collection


connected = False
client: MongoClient = None


def is_connected():
    global connected
    return connected


def collection(collection: str) -> Collection:
    global client
    return client[os.environ.get("DATABASE_NAME", "main")][collection]


def db_connect():
    global connected
    global client
    client = mongoengine_connect_db(
        username=os.environ.get("DATABASE_USERNAME", "admin"),
        password=os.environ.get("DATABASE_PASSWORD", "123456"),
        host=os.environ.get("DATABASE_HOST", "127.0.0.1"),
        port=int(os.environ.get("DATABASE_PORT", "27017")),
        db=os.environ.get("DATABASE_NAME", "main"),
        connectTimeoutMS=int(os.environ.get("MONGO_CONNECT_TIMEOUT_MS", "5000")),
        serverSelectionTimeoutMS=int(os.environ.get("MONGO_SELECTION_TIMEOUT_MS", "5000")),
    )

    try:
        client.server_info()
        print("MongoDB Connected")
        connected = True
    except Exception as e:
        print("ERROR: Can't connect MongoDB")
        print("Reconnecting MongoDB...")
        db_connect()

