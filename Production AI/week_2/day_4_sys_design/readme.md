### AI Microservice Demo: FastAPI, Microservices, and Production Best Practices

This repository contains a complete, copy-pasteable guide for a FastAPI AI inference microservice with Pydantic validation, dependency injection for an ML model, API-key protection, and caching using fastapi-cache2. It includes full code, virtual environment and install steps, Docker + Redis for production-like testing, VS Code run/debug configs, and troubleshooting.

### Table of Contents

1.  Project setup and opening in VS Code
2.  Virtual environment and package installation
3.  main.py (full commented code)
4.  Running locally (development)

### Project setup and opening in VS Code

Create a project folder and open it in VS Code:

```bash
mkdir ai-microservice-demo
cd ai-microservice-demo
```

### Virtual environment and package installation
Create and activate a virtual environment appropriate to your OS/shell.

# Windows PowerShell

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```


# Windows Command Prompt
```bash
python -m venv venv 
.\venv\Scripts\activate
```


# macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Uninstall any wrong cache packages, then install the correct packages:


```bash
# If you installed the wrong package before:
pip uninstall -y fastapi-cache fastapi_cache

# Install core packages
pip install fastapi uvicorn fastapi-cache2 pydantic

# Optional: Redis backend for production caching
pip install "fastapi-cache2[redis]" aioredis
```

Verify installations:

```bash
pip show fastapi-cache2
pip show fastapi
pip show uvicorn
```

## Running locally (development)

With your virtual environment activated, run:

```bash
uvicorn main:app --reload
```

You should see:

INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
Open the interactive docs at:

```bash
http://127.0.0.1:8000/docs
```


To test /predict in Swagger UI, add header X-API-Key: secret-api-key and request body:

```bash
{
  "feature1": 10.0,
  "feature2": 5.0
}
```

