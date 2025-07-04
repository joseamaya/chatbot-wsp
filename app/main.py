import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import get_settings
from app.database.connection import MongoDBConnection
from app.database.models.bot import Bot
from app.database.models.chat import Chat
from app.database.models.message import Message
from app.database.models.operator import Operator
from app.routes.bots import bots_router
from app.routes.whatsapp import whatsapp_router
from app.routes.auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDBConnection.connect_to_async_mongo()
    if os.getenv("ENVIRONMENT") == "development":
        from app.utils.ngrok import setup_ngrok
        print(setup_ngrok())
    yield
    if os.getenv("ENVIRONMENT") == "development":
        from pyngrok import ngrok
        ngrok.kill()
    await MongoDBConnection.close_async_mongo()


settings = get_settings()

app = FastAPI(lifespan=lifespan, debug=True)


@app.on_event("startup")
async def startup_event():
    client = AsyncIOMotorClient(settings.MONGO_DB_URL)
    await init_beanie(
        database=client[settings.MONGO_DB_NAME],
        document_models=[Bot, Chat, Message, Operator]
    )


app.include_router(whatsapp_router)
app.include_router(bots_router)
app.include_router(auth_router)
