from typing import List
from langchain.schema import Document
from langgraph.graph import MessagesState


class State(MessagesState):
    memory_context: str
    context: List[Document]
    answer: str
