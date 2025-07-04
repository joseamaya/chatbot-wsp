from langchain_core.runnables import RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.ai.config import GraphConfig
from app.ai.nodes import memory_extraction_node, memory_injection_node, retrieve, generate_response
from app.ai.retrievers import get_retriever_mongodb
from app.ai.statebot import StateBot


def create_workflow_graph():
    """
    Creates a workflow graph with all the necessary nodes and edges.

    Returns:
        StateGraph: The constructed graph before compilation
    """
    graph_builder = StateGraph(StateBot, config_schema=GraphConfig)
    graph_builder.add_edge(START, "memory_extraction_node")
    memories_retriever = get_retriever_mongodb(
        k=5,
        collection_name="memories",
        index_name="memories-vector-index",
        filters=["chat_id"]
    )

    async def call_memory_extraction(state: StateBot, config: RunnableConfig):
        return await memory_extraction_node(state, memories_retriever, config)

    async def call_memory_injection(state: StateBot, config: RunnableConfig):
        return await memory_injection_node(state, memories_retriever, config)

    graph_builder.add_node("memory_extraction_node", call_memory_extraction)
    graph_builder.add_node("memory_injection_node", call_memory_injection)

    rag_retriever = get_retriever_mongodb(
        k=5,
        collection_name="bots_rag",
        index_name="bots-vector-index",
        filters=["bot_id"]
    )

    async def call_retrieve(state: StateBot):
        return await retrieve(state, rag_retriever)

    graph_builder.add_node("retrieve", call_retrieve)
    graph_builder.add_node("generate_response", generate_response)
    graph_builder.add_edge("memory_extraction_node", "memory_injection_node")
    graph_builder.add_edge("memory_injection_node", "retrieve")
    graph_builder.add_edge("retrieve", "generate_response")
    graph_builder.add_edge("generate_response", END)
    return graph_builder

graph = create_workflow_graph().compile()
