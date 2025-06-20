import os
from enum import Enum

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Environment(str, Enum):
    LOCAL = "local"
    PRODUCTION = "production"


class Settings(BaseSettings):
    MONGO_DB_NAME: str = os.environ.get('MONGO_DB_NAME')
    WHATSAPP_TOKEN: str = os.environ.get('WHATSAPP_TOKEN')
    WHATSAPP_VERIFY_TOKEN: str = os.environ.get('WHATSAPP_VERIFY_TOKEN')
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v17.0"
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY')
    DEBUG: bool = False

    def get_whatsapp_api_headers(self) -> dict:
        """
        Retorna los headers necesarios para las llamadas a la API de WhatsApp
        """
        return {
            "Authorization": f"Bearer {self.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

class LocalConfig(Settings):
    MONGO_DB_URL: str = 'mongodb://localhost:32768/?directConnection=true'


class ProductionConfig(Settings):
    HOST: str = os.getenv('MONGO_HOST', 'localhost')
    USERNAME: str = os.getenv('MONGO_INITDB_ROOT_USERNAME', '')
    PASSWORD: str = os.getenv('MONGO_INITDB_ROOT_PASSWORD', '')
    PROTOCOL: str = os.getenv('PROTOCOL', 'mongodb')
    MONGO_DB_URL: str = f'{PROTOCOL}://{USERNAME}:{PASSWORD}@{HOST}'

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de la configuración
    """
    env = os.getenv("ENVIRONMENT", "local")
    settings = LocalConfig() if env == "local" else ProductionConfig()
    return settings
