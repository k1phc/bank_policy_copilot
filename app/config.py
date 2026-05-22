import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class Settings:
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "llama3.1:8b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "768"))
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://bank:bank@localhost:5432/bank_policy"
    )
    docs_path: str = os.getenv("DOCS_PATH", "sample_bank_docs")
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "logs/audit_log.jsonl")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_llm_client() -> OpenAI:
    s = get_settings()
    return OpenAI(base_url=s.llm_base_url, api_key=s.openai_api_key)
