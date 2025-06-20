from typing import Annotated
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.connection import MongoDBConnection

async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency para obtener la conexión a la base de datos
    """
    return MongoDBConnection.get_async_db()

DB = Annotated[AsyncIOMotorDatabase, Depends(get_database)]
