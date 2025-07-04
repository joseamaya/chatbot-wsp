from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database
from beanie import init_beanie
from app.config.settings import get_settings
from app.database.models.bot import Bot
from app.database.models.chat import Chat
from app.database.models.message import Message
from app.database.models.operator import Operator

settings = get_settings()

class MongoDBConnection:
    async_client: AsyncIOMotorClient = None
    async_db: AsyncIOMotorDatabase = None
    sync_client: MongoClient = None
    sync_db: Database = None

    @classmethod
    async def connect_to_async_mongo(cls):
        if cls.async_client is None:
            cls.async_client = AsyncIOMotorClient(settings.MONGO_DB_URL)
            cls.async_db = cls.async_client[settings.MONGO_DB_NAME]
            await init_beanie(
                database=cls.async_db,
                document_models=[Bot, Chat, Message, Operator]
            )

    @classmethod
    def connect_to_sync_mongo(cls):
        if cls.sync_client is None:
            cls.sync_client = MongoClient(settings.MONGO_DB_URL)
            cls.sync_db = cls.sync_client[settings.MONGO_DB_NAME]

    @classmethod
    async def close_async_mongo(cls):
        if cls.async_client is not None:
            cls.async_client.close()
            cls.async_client = None
            cls.async_db = None

    @classmethod
    def close_sync_mongo(cls):
        if cls.sync_client is not None:
            cls.sync_client.close()
            cls.sync_client = None
            cls.sync_db = None

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls.async_db is None:
            raise RuntimeError("La conexión asíncrona a MongoDB no está inicializada")
        return cls.async_db

    @classmethod
    def get_sync_db(cls) -> Database:
        if cls.sync_db is None:
            raise RuntimeError("La conexión síncrona a MongoDB no está inicializada")
        return cls.sync_db
