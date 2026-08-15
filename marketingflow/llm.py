import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv(override=True)


def ensure_api_key() -> None:
    load_dotenv(override=True)
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError(
            "GOOGLE_API_KEY is missing. Copy .env.example to .env and add your Gemini API key."
        )


def get_llm(temperature: float = 0.3) -> ChatGoogleGenerativeAI:
    ensure_api_key()
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=temperature,
        thinking_budget=0,
    )


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    ensure_api_key()
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
    )
