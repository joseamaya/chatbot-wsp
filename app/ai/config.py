from pydantic import BaseModel


class GraphConfig(BaseModel):
    thread_id: str
    chat_id: str
    prompt: str