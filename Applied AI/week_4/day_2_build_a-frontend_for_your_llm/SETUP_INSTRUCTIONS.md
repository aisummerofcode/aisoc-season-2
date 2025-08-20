# Complete Setup Instructions: Build a Simple Frontend for Your LLM App

## Prerequisites
- Python 3.8 or higher
- Git installed
- Internet connection for package downloads
- Text editor or IDE (VS Code recommended)

## Step-by-Step Setup Guide

### 1. Clone and Navigate to Project
```bash
# Clone the repository
git clone https://github.com/aisummerofcode/aisoc-season-2.git

# Navigate to the project directory
cd "aisoc-season-2/Applied AI/week_4/day_2_build_a-frontend_for_your_llm"

# Verify you're in the correct directory
ls -la  # Should see app.py, requirements.txt, src/ folder
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Verify activation - you should see (venv) in your terminal prompt
```

### 3. Install Dependencies
```bash
# Upgrade pip and build tools first (prevents many issues)
pip install --upgrade pip setuptools wheel build

# Install all required packages
pip install -r requirements.txt

# If Chainlit installation fails with jaraco.functools error:
pip uninstall jaraco.functools -y
pip install --upgrade build setuptools wheel
pip install chainlit

# Verify key packages are installed
pip list | grep -E "(chainlit|fastapi|chromadb|llama-index)"
```

### 4. Environment Configuration
Create a `.env` file in the project root directory:

```env
# Required: Get your free API key from https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# ChromaDB Server Configuration (Online Mode)
CHROMA_USE_SERVER=true
CHROMA_SERVER_HOST=127.0.0.1
CHROMA_SERVER_HTTP_PORT=8001
CHROMADB_SSL=false
CHROMA_PATH=./chroma_db

# Model Configuration
DEFAULT_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLAMA_3_3_70B=llama3-70b-8192
COLLECTION_NAME=chat_memory

# API Configuration
API_URL=http://127.0.0.1:8000
```

**Important:** Replace `your_groq_api_key_here` with your actual Groq API key from https://console.groq.com/keys

### 5. Install ChromaDB Server
```bash
# Install ChromaDB server component
pip install "chromadb>=0.5.0"

# Verify installation
chroma --help
```

### 6. Copy the Updated Code Files
Replace the existing files with the commented versions:

- Copy `chainlit_client.py` to project root
- Copy `helpers.py` to `src/helpers.py` 
- Copy `app_chainlit_demo.py` to project root (optional reference)

## Running the Application

### Terminal 1: Start ChromaDB Server (MUST BE FIRST!)
```bash
# Navigate to project directory
cd "aisoc-season-2/Applied AI/week_3/day_6_chat_engine"

# Start ChromaDB server
chroma run --path "./chroma_db" --host 127.0.0.1 --port 8001

# Look for this message: "Running Chroma on http://127.0.0.1:8001"
# Keep this terminal open!
```

### Terminal 2: Start FastAPI Backend
```bash
# Navigate to project directory
cd "aisoc-season-2/Applied AI/week_3/day_6_chat_engine"

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start FastAPI server
python app.py

# Look for: "Uvicorn running on http://127.0.0.1:8000"
# Keep this terminal open!
```

### Terminal 3: Start Chainlit Frontend
```bash
# Navigate to project directory
cd "aisoc-season-2/Applied AI/week_3/day_6_chat_engine"

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start Chainlit on different port to avoid conflicts
chainlit run chainlit_client.py --port 8080

# Look for: "Your app is available at http://localhost:8080"
# Open this URL in your browser!
```

## Testing the Application

### 1. Health Check
Open your browser and visit: http://127.0.0.1:8000/health/chroma

You should see:
```json
{"ok": true, "collection_count": 0}
```

### 2. Test the Frontend
1. Open http://localhost:8080 in your browser
2. You should see the Chainlit interface with welcome messages
3. Click "📤 Upload Documents" button
4. Upload a sample document (PDF, TXT, or DOCX)
5. Wait for "✅ Upload Successful!" message
6. Ask a question about your uploaded document
7. Watch the streaming response appear in real-time

## Troubleshooting Common Issues

### ❌ "Could not connect to Chroma server"
**Solution:** 
- Ensure ChromaDB server is running first (Terminal 1)
- Check that port 8001 is not blocked by firewall
- Verify CHROMA_SERVER_HTTP_PORT in .env matches the port used

### ❌ "Port already in use"
**Solutions:**
- Kill existing processes: `netstat -ano | findstr :8000` (Windows) or `lsof -ti:8000` (Mac/Linux)
- Use different ports:
  ```bash
  # For FastAPI
  uvicorn app:app --port 8002
  
  # For Chainlit
  chainlit run chainlit_client.py --port 8081
  ```

### ❌ "Action requires payload"
**Solution:** Use the updated `chainlit_client.py` file provided - it includes the payload fix for newer Chainlit versions.

### ❌ "File upload failed"
**Solutions:**
- Check file format (only PDF, TXT, DOCX, MD, CSV, JSON supported)
- Ensure file size is under 25MB
- Verify FastAPI server is running and reachable

### ❌ "No response from chat"
**Solutions:**
- Check Groq API key is valid and has credits
- Verify you uploaded documents first
- Check FastAPI server logs for errors

### ❌ "ModuleNotFoundError: No module named 'groq'"
**Solution:**
```bash
pip install groq
# or
pip install llama-index-llms-groq
```

### ❌ Chainlit installation fails
**Solution:**
```bash
pip uninstall jaraco.functools -y
pip install --upgrade build setuptools wheel
pip install chainlit
```

## Development Tips

### Viewing Logs
- FastAPI logs appear in Terminal 2
- ChromaDB logs appear in Terminal 1
- Check `logs/status_logs.log` for detailed application logs

### Restarting Services
If you need to restart:
1. Stop all terminals (Ctrl+C)
2. Start ChromaDB first (Terminal 1)
3. Start FastAPI second (Terminal 2)
4. Start Chainlit last (Terminal 3)

### Testing Different Models
You can change models by typing in the chat:
```
bot=MyAssistant; model=mixtral-8x7b-32768
```

### Clearing Data
To start fresh:
```bash
# Stop all services first
rm -rf chroma_db/  # Deletes all stored documents
# Restart services
```

## Production Deployment Considerations

### Security
- Use environment-specific .env files
- Implement proper authentication
- Add rate limiting
- Validate all inputs
- Use HTTPS in production

### Scalability
- Deploy ChromaDB on separate server
- Use cloud vector databases (Pinecone, Weaviate)
- Implement load balancing
- Add caching layer
- Monitor resource usage

### Monitoring
- Add health check endpoints
- Implement logging aggregation
- Set up error tracking
- Monitor API usage and costs
- Track user engagement metrics

## Next Steps

Once you have the basic application running:

1. **Experiment with different document types**
2. **Try various LLM models and settings**
3. **Implement user authentication**
4. **Add conversation persistence**
5. **Deploy to cloud platforms**
6. **Create custom UI themes**
7. **Add support for more file formats**
8. **Implement admin dashboard**

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the terminal logs for error messages
3. Verify all environment variables are set correctly
4. Ensure all three services are running
5. Test the health check endpoint first

Remember: The order of starting services matters - ChromaDB first, then FastAPI, then Chainlit!
