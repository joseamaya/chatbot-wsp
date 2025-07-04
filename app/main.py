import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.database.connection import MongoDBConnection
from app.routes.bots import bots_router
from app.routes.whatsapp import whatsapp_router
from app.routes.auth import auth_router
from app.routes.websocket import websocket_router


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

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://chatbot-wsp-q6j0.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(whatsapp_router)
app.include_router(bots_router)
app.include_router(auth_router)
app.include_router(websocket_router)
