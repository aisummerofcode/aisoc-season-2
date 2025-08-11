# main.py
"""
Demo FastAPI app for teaching:
 - Pydantic validation for request/response schemas
 - Dependency Injection (DI) for managing ML model instances
 - Simple API key authentication for endpoint security
 - Caching using fastapi-cache2 (InMemory for development, Redis example commented)
 - Clear, inline comments to explain each code block
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import APIKeyHeader

# fastapi-cache2 imports (ensure fastapi-cache2 is installed)
from fastapi_cache import FastAPICache, cache
from fastapi_cache.backends.inmemory import InMemoryBackend
# If you plan to use Redis in production, uncomment these:
# from aioredis import from_url
# from fastapi_cache.backends.redis import RedisBackend

# Create the FastAPI application instance
app = FastAPI(title="AI Inference Microservice Demo")

# --------------------------------------------------------------------
# 1. Simple API Key Security (demo only)
# --------------------------------------------------------------------
# In production, load from env vars or secret manager. Do NOT hardcode secrets.
API_KEY = os.getenv("DEMO_API_KEY", "secret-api-key")  # demo default
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    FastAPI dependency that enforces the presence and correctness of 'X-API-Key'.
    Raises 401 Unauthorized if missing or incorrect.
    """
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Provide 'X-API-Key' header."
        )
    return api_key

# --------------------------------------------------------------------
# 2. Pydantic models
# --------------------------------------------------------------------
class InputData(BaseModel):
    """Schema for incoming prediction requests."""
    feature1: float
    feature2: float

class Prediction(BaseModel):
    """Schema for prediction responses."""
    result: float

# --------------------------------------------------------------------
# 3. Example ML model and DI
# --------------------------------------------------------------------
class MLModel:
    """Example model wrapper. Replace with actual model load and inference."""
    def __init__(self):
        # In real usage, load your model once here.
        # Example: self.model = joblib.load("model.joblib")
        print("INFO: MLModel instance created (demo).")

    def predict(self, data: InputData) -> Prediction:
        """Perform a simple weighted-sum prediction (replace with real model inference)."""
        value = data.feature1 * 0.6 + data.feature2 * 0.4
        return Prediction(result=value)

def get_model():
    """
    Dependency function that returns an MLModel instance.
    For a singleton pattern, create MODEL = MLModel() at module level and return it here.
    """
    return MLModel()

# --------------------------------------------------------------------
# 4. Cache initialization using fastapi-cache2
# --------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    """
    Initialize the cache backend on startup.
    InMemoryBackend is fine for development. For production use RedisBackend (example below).
    """
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    print("INFO: FastAPICache initialized with InMemoryBackend (dev).")

    # Redis example (uncomment to use Redis):
    # redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    # redis = from_url(redis_url, encoding="utf-8", decode_responses=True)
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # print(f"INFO: FastAPICache initialized with RedisBackend at {redis_url}.")
    


# --------------------------------------------------------------------
# 5. Prediction endpoint
# --------------------------------------------------------------------
@app.post("/predict", response_model=Prediction, status_code=status.HTTP_200_OK)
@cache(expire=30)  # caches identical requests for 30 seconds
async def predict(
    data: InputData,
    model: MLModel = Depends(get_model),
    api_key: str = Depends(verify_api_key) 
):
    """
    Prediction endpoint:
    - Validates input via Pydantic
    - Requires API key via verify_api_key dependency
    - Uses model provided by get_model dependency
    - Responses are cached for 'expire' seconds
    """
    print(f"INFO: Processing prediction for {data.dict()}")
    return model.predict(data)