import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.connection import MongoDBConnection
from app.routes.bots import bots_router
from app.routes.whatsapp import whatsapp_router
from app.utils.ngrok import setup_ngrok


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDBConnection.connect_to_async_mongo()
    if os.getenv("ENVIRONMENT") == "development":
        print(setup_ngrok())
    yield
    if os.getenv("ENVIRONMENT") == "development":
        from pyngrok import ngrok
        ngrok.kill()
    await MongoDBConnection.close_async_mongo()


app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(whatsapp_router)
app.include_router(bots_router)
