from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.app_config import app_config


router = APIRouter(prefix="/api/config", tags=["config"])


class OpenAIKeyRequest(BaseModel):
    api_key: str


@router.get("/openai")
async def get_openai_key_status():
    """Return whether an OpenAI API key is configured (masked)."""
    return app_config.get_openai_key_metadata()


@router.post("/openai")
async def set_openai_key(payload: OpenAIKeyRequest):
    """Persist a new OpenAI API key for subsequent requests."""
    try:
        app_config.set_openai_api_key(payload.api_key)
        return app_config.get_openai_key_metadata()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
