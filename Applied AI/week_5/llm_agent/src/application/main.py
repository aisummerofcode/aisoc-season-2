# Import necessary modules
import os, secrets, uvicorn
from fastapi import FastAPI, status, Depends
from fastapi.security import HTTPBasic
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import Settings, get_setting
from contextlib import asynccontextmanager
from src.utilities.Printer import printer
from src.config.appconfig import env_config
from src.application.routes import agentic_router

# Get application settings from the settings module
settings = get_setting()

# Description for API documentation
description = f"""
{settings.API_STR} helps you do awesome stuff. 🚀
"""



# Define a context manager for the application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application lifespan.
    This function initializes and cleans up resources during the application's lifecycle.
    """
    # STARTUP Call Check routine

    print(running_mode)
    print()
    print()
    printer(" ⚡️🚀 Agentic AI Server::Started", "sky_blue")
    print()
    printer(" ⚡️🏎  Agentic AI Server::Running", "sky_blue")
    yield
    printer(" 🔴 Agentic AI Server::SHUTDOWN", "red")

# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=description,
    openapi_url=f"{settings.API_STR}/openapi.json",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    contact={
        "name": "AISummerOfCode",
        "url": "https://www.aisummerofcode.com/",
        "email": "hello@aisummerofcode.com",
    },
    lifespan=lifespan,
)



# Configure for development or production mode
if env_config.environment in ["development", "staging"]:
    running_mode = f"  👩‍💻 🛠️  Running in::{env_config.environment} mode"
else:
    # app.add_middleware(HTTPSRedirectMiddleware)
    running_mode = "  🏭 ☁  Running in::production mode"

# Define allowed origins for CORS
origins = [
    "*",
]

# Instantiate basicAuth
security = HTTPBasic()

# Add middleware to allow CORS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Define a health check endpoint
@app.get("/", status_code=status.HTTP_200_OK)
def index():
    return "pong"


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return "healthy"


app.include_router(agentic_router,prefix=settings.API_STR,  
                   tags=["Chat"],dependencies=[
        Depends(get_setting),
    ],)

if __name__ == "__main__":
    # Retrieve environment variables for host, port, and timeout
    timeout_keep_alive = int(os.getenv("TIMEOUT", 6000))

    # Run the application with the specified host, port, and timeout
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(env_config.port),
        timeout_keep_alive=timeout_keep_alive,
    )
