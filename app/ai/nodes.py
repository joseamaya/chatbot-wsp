import logging

from langchain_core.runnables import RunnableConfig

from app.ai.chains import get_memory_chain, get_character_chain
from app.ai.statebot import StateBot

logger = logging.getLogger(__name__)


async def memory_extraction_node(state: StateBot, retriever, config: RunnableConfig):
    chain = get_memory_chain()
    response = await chain.ainvoke({"message": state["messages"][-1]})
    if response.is_important and retriever:
        config = config.get("configurable")
        chat_id = config.get("chat_id")
        try:
            await retriever.vectorstore.aadd_texts(
                texts=[response.formatted_memory],
                metadatas=[{"chat_id": chat_id}]
            )
        except Exception as e:
            print(f"Error almacenando memoria: {str(e)}")
    return {}

async def memory_injection_node(state: StateBot, retriever, config: RunnableConfig):
    if not retriever:
        return {"memory_context": ""}
    config = config.get("configurable")
    chat_id = config.get("chat_id")
    last_message = state["messages"][-1].content
    try:
        relevant_docs = await retriever.ainvoke(
            last_message,
            pre_filter={"chat_id": chat_id}
        )
        memory_context = "\n".join(doc.page_content for doc in relevant_docs)
        return {"memory_context": memory_context}
    except Exception as e:
        print(f"Error recuperando memorias: {str(e)}")
        return {"memory_context": ""}

async def retrieve(state: StateBot, retriever):
    if not retriever:
        return {"context": []}
    query = state["messages"][-1]
    try:
        retrieved_docs = await retriever.ainvoke(query.content)
        return {"context": retrieved_docs}
    except Exception as e:
        print(f"Error en retrieve: {str(e)}")
        return {"context": []}

async def generate_response(state: StateBot, config: RunnableConfig):
    config = config.get("configurable")
    prompt = config.get("prompt", "")
    memory_context = state.get('memory_context')
    docs_content = "\n\n".join(doc.page_content for doc in state.get("context", []))
    chain = get_character_chain(prompt)
    response = await chain.ainvoke(
        {
            "messages": state['messages'],
            "context": docs_content,
            "memory_context": memory_context,
        },
        config,
    )
    return {"answer": response.content, "messages": response}
