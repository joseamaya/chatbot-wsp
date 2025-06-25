import os

from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_community.document_loaders import TextLoader

from app.database.models.bot import Bot
from app.schemas.bot import BotCreate, BotResponse
from app.ai.retrievers import get_retriever_mongodb
from app.ai.splitters import get_narrative_splitter

bots_router = APIRouter(
    prefix="/bots",
    tags=["bots"]
)

async def save_temp_file(info_bytes: bytes, filename: str) -> str:
    """Guarda un archivo temporal y retorna su ruta."""
    temp_file_name = f"temp_{filename}"
    temp_file_path = os.path.join("/tmp", temp_file_name)
    with open(temp_file_path, "wb+") as f:
        f.write(info_bytes)
    return temp_file_path

async def process_documents(file_path: str):
    """Procesa los documentos y los añade al vector store."""
    loader = TextLoader(file_path)
    documents = loader.load()
    splitter = get_narrative_splitter()
    docs = splitter.split_documents(documents)

    vector_store = get_retriever_mongodb(
        k=5,
        collection_name="bots_rag",
        index_name="bots-vector-index"
    ).vectorstore
    vector_store.add_documents(documents=docs)


@bots_router.post("/{id}/upload-info")
async def upload_info(info: UploadFile = File(...)):
    """
    Sube información para el bot y la procesa para RAG.

    Args:
        info: Archivo a procesar

    Returns:
        dict: Información del resultado

    Raises:
        HTTPException: Si hay error en la subida o procesamiento
    """
    try:
        info_bytes = await info.read()
        await info.seek(0)
        temp_file_path = await save_temp_file(info_bytes, info.filename)
        await process_documents(temp_file_path)
        os.remove(temp_file_path)
        return {"status": "success", "message": "Información procesada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento: {str(e)}")

@bots_router.post("/", response_model=BotResponse, status_code=201)
async def create_bot(bot_data: BotCreate):
    """
    Crea un nuevo bot.

    Args:
        bot_data: Datos del bot a crear

    Returns:
        BotResponse: Datos del bot creado

    Raises:
        HTTPException: Si hay error en la creación o el nombre ya existe
    """
    try:
        bot = Bot(
            name=bot_data.name,
            prompt=bot_data.prompt,
            whatsapp_phone_number_id=bot_data.whatsapp_phone_number_id,
            whatsapp_token=bot_data.whatsapp_token,
            whatsapp_verify_token=bot_data.whatsapp_verify_token
        )

        await bot.save()

        return BotResponse(
            id=str(bot.id),
            name=bot.name,
            prompt=bot.prompt,
            whatsapp_phone_number_id=bot.whatsapp_phone_number_id,
            whatsapp_verify_token=bot.whatsapp_verify_token,
            created_at=bot.created_at,
            updated_at=bot.updated_at,
            is_active=bot.is_active
        )
    except Exception as e:
        if "duplicate key error" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un bot con el nombre '{bot_data.name}'"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el bot: {str(e)}"
        )
