from contextlib import asynccontextmanager

from fastapi import FastAPI
from routes.whatsapp import whatsapp_router
from database.connection import MongoDBConnection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDBConnection.connect_to_async_mongo()
    yield
    await MongoDBConnection.close_async_mongo()


app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(whatsapp_router)
