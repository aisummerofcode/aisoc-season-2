# Instructor Troubleshooting Guide: Build a Simple Frontend for Your LLM App

## Pre-Class Preparation Checklist

### 30 Minutes Before Class
- [ ] Test all three services on your machine
- [ ] Prepare 3-4 sample documents (PDF, TXT, DOCX)
- [ ] Have backup Groq API keys ready
- [ ] Test internet connectivity and download speeds
- [ ] Prepare backup environments (Docker containers or cloud instances)
- [ ] Print troubleshooting quick reference cards

### 10 Minutes Before Class
- [ ] Start your demo environment
- [ ] Test file upload and chat functionality
- [ ] Have terminal windows ready for live demonstration
- [ ] Prepare backup code files on USB/cloud storage

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
**Instructor Action:** Walk around and check individual terminals

#### ❌ Python Version Issues
**Symptoms:** "Python not found" or version conflicts
**Solutions:**
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.9 -m venv venv
python3.10 -m venv venv
```
**Instructor Action:** Have students use `python3` explicitly

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
**Instructor Action:** Have pre-built environments ready

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
**Instructor Action:** Pair struggling students with successful ones

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
**Instructor Action:** 
- Show alternative embedded mode setup
- Have Docker ChromaDB ready as backup

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
**Instructor Action:** Have simplified app.py without complex imports

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
**Instructor Action:** Show how to hardcode API URL for testing

### 4. Runtime Issues

#### ❌ File Upload Fails
**Symptoms:** "Could not read file bytes", upload timeout
**Quick Diagnosis:**
- Check file size (<25MB)
- Verify file format (PDF, TXT, DOCX only)
- Test with simple .txt file first
**Instructor Action:** Provide known-good sample files

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
**Instructor Action:** Have backup API keys, show rate limiting

## Class Management Strategies

### For Mixed Skill Levels
1. **Pair Programming:** Match experienced with beginners
2. **Checkpoint System:** Stop class at key milestones
3. **Multiple Paths:** Offer Docker alternative for struggling students
4. **Extension Activities:** Give advanced students additional challenges

### Time Management
- **Setup Phase (20 min):** Don't let anyone fall more than 5 minutes behind
- **Code Review (30 min):** Focus on concepts, not typing speed
- **Hands-on (20 min):** Circulate constantly, help proactively
- **Testing (8 min):** Have working examples ready to show

### Backup Plans

#### Plan A: Full Setup (Ideal)
All students run three services locally

#### Plan B: Shared ChromaDB (Fallback)
- Run ChromaDB on instructor machine
- Students connect to shared instance
- Update CHROMA_SERVER_HOST in .env

#### Plan C: Docker Containers (Emergency)
```bash
# Pre-built containers
docker run -p 8001:8001 chromadb/chroma
docker run -p 8000:8000 your-fastapi-image
```

#### Plan D: Cloud Deployment (Last Resort)
- Deploy to Replit, CodeSandbox, or similar
- Students access via browser
- Focus on concepts rather than setup

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

## Student Questions & Answers

### Technical Questions

**Q: "Why do we need three separate services?"**
A: "This is called microservices architecture. Each service has one job - ChromaDB stores vectors, FastAPI handles logic, Chainlit provides UI. This scales better than monolithic apps."

**Q: "Can we use OpenAI instead of Groq?"**
A: "Absolutely! Just change the LLM client in helpers.py. Groq is faster and cheaper for learning, but OpenAI works the same way."

**Q: "What if ChromaDB server crashes in production?"**
A: "Great question! In production, you'd use managed services like Pinecone or Weaviate, or run ChromaDB in Kubernetes with auto-restart."

### Conceptual Questions

**Q: "How is this different from ChatGPT?"**
A: "ChatGPT uses its training data. Our app uses YOUR documents. It's like having a personal ChatGPT trained on your specific knowledge base."

**Q: "Why is streaming important?"**
A: "User experience! Instead of waiting 10 seconds for a complete response, users see words appearing immediately. It feels more interactive."

**Q: "How do embeddings work?"**
A: "Think of embeddings as coordinates in meaning-space. Similar concepts have similar coordinates. We find documents with coordinates close to the user's question."

## Emergency Procedures

### If Internet Goes Down
1. Switch to offline mode with pre-downloaded models
2. Use embedded ChromaDB instead of server mode
3. Focus on code explanation rather than live demo
4. Have printed code handouts ready

### If Groq API Fails
1. Switch to local LLM (Ollama)
2. Use mock responses for demonstration
3. Focus on architecture rather than actual responses
4. Have backup API keys from different providers

### If Multiple Students Struggle
1. Pause class for group troubleshooting
2. Switch to pair programming mode
3. Use shared screen for collective debugging
4. Move to conceptual discussion while fixing issues

## Post-Class Follow-up

### Immediate (End of Class)
- [ ] Share troubleshooting guide with students
- [ ] Provide working code repository
- [ ] Schedule office hours for struggling students
- [ ] Collect feedback on technical difficulties

### Within 24 Hours
- [ ] Send follow-up email with resources
- [ ] Update setup instructions based on issues encountered
- [ ] Prepare improved version for next class
- [ ] Document new issues for future reference

### For Next Class
- [ ] Improve pre-class setup instructions
- [ ] Prepare more backup environments
- [ ] Create video tutorials for common issues
- [ ] Consider alternative tools if problems persist

## Success Metrics

### Class Success Indicators
- 80%+ of students have working application by end of class
- Students can upload documents and get responses
- Students understand the architecture
- Students can troubleshoot basic issues independently

### Individual Success Indicators
- Student can explain the three-service architecture
- Student can modify configuration (model, bot name)
- Student can upload different file types
- Student can identify and fix common errors

Remember: The goal is learning, not perfect execution. If students understand the concepts and architecture, the class is successful even if some technical issues remain!
