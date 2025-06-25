from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.bots import bots_router
from app.routes.whatsapp import whatsapp_router
from app.database.connection import MongoDBConnection
from app.utils import setup_ngrok


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDBConnection.connect_to_async_mongo()
    print(setup_ngrok())
    yield
    await MongoDBConnection.close_async_mongo()


app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(whatsapp_router)
app.include_router(bots_router)
