import os

from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_community.document_loaders import TextLoader

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