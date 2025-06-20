from typing import Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ai.prompts import MEMORY_ANALYSIS_PROMPT, CHARACTER_PROMPT


class MemoryAnalysis(BaseModel):
    is_important: bool = Field(
        ...,
        description="Whether the message is important enough to be stored as a memory",
    )
    formatted_memory: Optional[str] = Field(
        ..., description="The formatted memory to be stored"
    )

class InterestsOutput(BaseModel):
    interests: list[str] = Field(..., description="Lista de intereses extraídos del mensaje del usuario")


def get_memory_chain():
    model = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(MemoryAnalysis)
    prompt = ChatPromptTemplate.from_template(MEMORY_ANALYSIS_PROMPT)
    return prompt | model


def get_character_chain():
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CHARACTER_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt | model