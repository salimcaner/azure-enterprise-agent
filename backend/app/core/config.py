from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    project_endpoint: str
    api_key: str
    model_deployment: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT", ""),
        api_key=os.getenv("FOUNDRY_API_KEY", ""),
        model_deployment=os.getenv("MODEL_DEPLOYMENT_NAME", ""),
    )


settings = get_settings()
