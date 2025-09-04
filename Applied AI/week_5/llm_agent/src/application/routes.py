import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from src.config.settings import get_setting
from src.application.datamodels import *
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.config.appconfig import env_config
# Get application settings from the settings module
settings = get_setting()

agentic_router = APIRouter()

@agentic_router.post("/chat", response_model=ChatResponse)
async def chat(chat_payload: ChatPayload, x_api_key: Optional[str] = Header(None, alias="X-API-KEY")):
    """
    Chat with the AI model.
    """
    if x_api_key != env_config.x_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return await chat_payload.model_dump_json()