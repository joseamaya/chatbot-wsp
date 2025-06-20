from langchain_openai import OpenAIEmbeddings

def get_embeddings():
    embeddings = OpenAIEmbeddings()
    return embeddings