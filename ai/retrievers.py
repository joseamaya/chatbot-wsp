from ai.mongo_db_vector_store import get_mongo_db_vector_store


def get_retriever_mongodb(k: int, collection_name: str, index_name: str, filters: list):
    vector_store = get_mongo_db_vector_store().get_instance(
        collection_name=collection_name,
        index_name=index_name,
        filters=filters
    )
    return vector_store.as_retriever(search_kwargs={"k": k})
