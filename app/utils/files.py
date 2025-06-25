import os
from langchain_community.document_loaders import TextLoader
from app.ai.splitters import get_narrative_splitter
from app.ai.retrievers import get_retriever_mongodb


async def save_temp_file(info_bytes: bytes, filename: str) -> str:
    """
    Guarda un archivo temporal y retorna su ruta.
    
    Args:
        info_bytes: Bytes del archivo a guardar
        filename: Nombre del archivo
        
    Returns:
        str: Ruta del archivo temporal guardado
    """
    temp_file_name = f"temp_{filename}"
    temp_file_path = os.path.join("/tmp", temp_file_name)
    with open(temp_file_path, "wb+") as f:
        f.write(info_bytes)
    return temp_file_path


async def process_documents(file_path: str, collection_name: str = "bots_rag", index_name: str = "bots-vector-index"):
    """
    Procesa los documentos y los añade al vector store.
    
    Args:
        file_path: Ruta del archivo a procesar
        collection_name: Nombre de la colección en MongoDB para el vector store
        index_name: Nombre del índice para el vector store
    """
    loader = TextLoader(file_path)
    documents = loader.load()
    splitter = get_narrative_splitter()
    docs = splitter.split_documents(documents)

    vector_store = get_retriever_mongodb(
        k=5,
        collection_name=collection_name,
        index_name=index_name
    ).vectorstore
    vector_store.add_documents(documents=docs)
