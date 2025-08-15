from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field("")
    name: str = Field("")
    location: Optional[str] = Field("lagos, Nigeria")