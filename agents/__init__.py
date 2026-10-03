import os
from langchain_groq import ChatGroq

def get_groq_llm() -> ChatGroq:
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    return ChatGroq(
        temperature=0.1,
        model_name="openai/gpt-oss-120b",
        groq_api_key=groq_api_key
    )

from agents.manager_agent import create_manager_agent
from agents.analyst_agent import create_analyst_agent
from agents.reporter_agent import create_reporter_agent

__all__ = [
    "get_groq_llm",
    "create_manager_agent",
    "create_analyst_agent",
    "create_reporter_agent"
]
