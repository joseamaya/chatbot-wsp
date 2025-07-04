import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.database.models.bot import Bot
from app.database.models.operator import Operator
from app.schemas.bot import BotCreate, BotResponse
from app.utils.files import save_temp_file, process_documents
from app.utils.auth import get_current_operator

bots_router = APIRouter(
    prefix="/bots",
    tags=["bots"]
)

@bots_router.post("/{id}/upload-info")
async def upload_info(
    id: str,
    info: UploadFile = File(...),
    current_operator: Operator = Depends(get_current_operator)
):
    """
    Sube información para el bot y la procesa para RAG.

    Args:
        id: ID del bot
        info: Archivo a procesar
        current_operator: Operador autenticado (inyectado automáticamente)

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
async def create_bot(
    bot_data: BotCreate,
    current_operator: Operator = Depends(get_current_operator)
):
    """
    Crea un nuevo bot.

    Args:
        bot_data: Datos del bot a crear
        current_operator: Operador autenticado (inyectado automáticamente)

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
