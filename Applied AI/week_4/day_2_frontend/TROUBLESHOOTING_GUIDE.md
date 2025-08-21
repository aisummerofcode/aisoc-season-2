## Common Student Issues & Solutions

### 1. Environment Setup Issues

#### ❌ Virtual Environment Problems
**Symptoms:** Students can't activate venv or see (venv) in prompt
**Solutions:**
```bash
# Windows - try different activation methods
venv\Scripts\activate.bat
# or
venv\Scripts\Activate.ps1

# Mac/Linux - check shell type
source venv/bin/activate
# or for fish shell
source venv/bin/activate.fish
```

#### ❌ Python Version Issues
**Symptoms:** "Python not found" or version conflicts
**Solutions:**
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.10 -m venv venv
python3.11 -m venv venv
```

### 2. Package Installation Issues

#### ❌ Chainlit Installation Fails
**Symptoms:** jaraco.functools error, build failures
**Solutions:**
```bash
# Standard fix
pip uninstall jaraco.functools -y
pip install --upgrade build setuptools wheel
pip install chainlit

# Alternative: use conda
conda install -c conda-forge chainlit

# Last resort: use specific version
pip install chainlit==1.0.0
```
#### ❌ ChromaDB Installation Issues
**Symptoms:** Compilation errors, missing dependencies
**Solutions:**
```bash
# Try different installation methods
pip install chromadb --no-cache-dir
pip install "chromadb>=0.5.0" --force-reinstall

# For M1 Macs
pip install chromadb --no-deps
pip install hnswlib pydantic fastapi uvicorn
```

### 3. Service Startup Issues

#### ❌ ChromaDB Server Won't Start
**Symptoms:** "Command not found", port binding errors
**Quick Diagnosis:**
```bash
# Check if ChromaDB is installed
chroma --help

# Check if port is in use
netstat -an | grep 8001  # Windows/Linux
lsof -i :8001           # Mac

# Try different port
chroma run --port 8002 --path "./chroma_db"
```
#### ❌ FastAPI Won't Start
**Symptoms:** Import errors, port conflicts
**Quick Diagnosis:**
```bash
# Check imports manually
python -c "import fastapi; print('FastAPI OK')"
python -c "from src.helpers import init_chroma; print('Helpers OK')"

# Check port availability
netstat -an | grep 8000

# Start on different port
uvicorn app:app --port 8002
```

#### ❌ Chainlit Connection Issues
**Symptoms:** Can't connect to FastAPI, timeout errors
**Quick Diagnosis:**
```bash
# Test FastAPI directly
curl http://127.0.0.1:8000/health/chroma

# Check API_URL in environment
echo $API_URL  # Linux/Mac
echo %API_URL% # Windows
```
### 4. Runtime Issues

#### ❌ File Upload Fails
**Symptoms:** "Could not read file bytes", upload timeout
**Quick Diagnosis:**
- Check file size (<25MB)
- Verify file format (PDF, TXT, DOCX only)
- Test with simple .txt file first

#### ❌ Chat Responses Don't Work
**Symptoms:** No response, error messages, timeout
**Quick Diagnosis:**
```bash
# Check Groq API key
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models

# Test with simple query
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"Hello","model":"llama3-70b-8192","chat_uid":"test","chatbot_name":"Assistant"}'
```

## Quick Reference Commands

### Health Checks
```bash
# ChromaDB
curl http://127.0.0.1:8001/api/v1/heartbeat

# FastAPI
curl http://127.0.0.1:8000/health/chroma

# Chainlit
# Open http://localhost:8080 in browser
```

### Process Management
```bash
# Kill processes by port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill processes by port (Mac/Linux)
lsof -ti:8000 | xargs kill -9

# Kill all Python processes (emergency)
pkill -f python
```

### Quick Fixes
```bash
# Reset ChromaDB
rm -rf chroma_db/
mkdir chroma_db

# Reset Python environment
deactivate
rm -rf venv/
python -m venv venv
```
