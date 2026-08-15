from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from .config import get_settings


def ensure_api_key() -> None:
    get_settings(require_google_api_key=True)


def get_llm(temperature: float = 0.3) -> ChatGoogleGenerativeAI:
    settings = get_settings(require_google_api_key=True)
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        temperature=temperature,
        thinking_budget=0,
    )


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    settings = get_settings(require_google_api_key=True)
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model
    )
