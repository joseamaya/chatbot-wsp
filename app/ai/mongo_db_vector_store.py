from typing import Optional, Dict, ClassVar
from functools import lru_cache
from langchain_mongodb import MongoDBAtlasVectorSearch

from app.ai.embeddings import get_embeddings
from app.database.connection import MongoDBConnection


class MongoDBVectorStore:
    """Clase para manejar múltiples instancias de MongoDBAtlasVectorSearch."""

    _instances: ClassVar[Dict[str, MongoDBAtlasVectorSearch]] = {}
    EMBEDDING_DIMENSION = 1536

    @classmethod
    def get_instance(
        cls,
        collection_name: str,
        index_name: str,
        filters: Optional[list] = None
    ) -> MongoDBAtlasVectorSearch:
        """Obtiene o crea una instancia de MongoDBAtlasVectorSearch para una colección específica."""
        instance_key = f"{collection_name}:{index_name}"

        if instance_key not in cls._instances:
            try:
                db = MongoDBConnection.get_sync_db()
            except:
                MongoDBConnection.connect_to_sync_mongo()
                db = MongoDBConnection.get_sync_db()
            collection = db[collection_name]
            vector_store = MongoDBAtlasVectorSearch(
                collection=collection,
                embedding=get_embeddings(),
                index_name=index_name,
                relevance_score_fn="cosine"
            )
            existing_indexes = collection.list_search_indexes()
            existing_names = [idx["name"] for idx in existing_indexes]
            if index_name not in existing_names:
                try:
                    vector_store.create_vector_search_index(
                        dimensions=cls.EMBEDDING_DIMENSION,
                        filters=filters or []
                    )
                    print(f"Índice vectorial '{index_name}' creado exitosamente")
                except Exception as e:
                    print(f"Warning: No se pudo crear el índice vectorial: {e}")
            else:
                print(f"El índice vectorial '{index_name}' ya existe")
            cls._instances[instance_key] = vector_store
        return cls._instances[instance_key]


@lru_cache
def get_mongo_db_vector_store() -> MongoDBVectorStore:
    """Retorna la instancia singleton de MongoDBVectorStore."""
    return MongoDBVectorStore()
