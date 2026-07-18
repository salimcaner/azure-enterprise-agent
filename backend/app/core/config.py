from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    project_endpoint: str
    api_key: str
    model_deployment: str
    embedding_deployment: str
    search_endpoint: str
    search_api_key: str
    search_index_name: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT", ""),
        api_key=os.getenv("FOUNDRY_API_KEY", ""),
        model_deployment=os.getenv("MODEL_DEPLOYMENT_NAME", ""),
        embedding_deployment=os.getenv("EMBEDDING_DEPLOYMENT_NAME", ""),
        search_endpoint=os.getenv("SEARCH_ENDPOINT", ""),
        search_api_key=os.getenv("SEARCH_API_KEY", ""),
        search_index_name=os.getenv("SEARCH_INDEX_NAME", ""),
    )


settings = get_settings()
