"""
Chainlit Frontend Client for RAG Chat Application

This file creates a ChatGPT-like interface using Chainlit that connects to our FastAPI backend.
It provides a modern chat interface with document upload capabilities and streaming responses.

Key Features:
- Session management with unique chat UIDs for each conversation
- File upload functionality for document indexing
- Real-time streaming chat responses from the backend
- Dynamic configuration (model selection, bot name customization)
- Comprehensive error handling and user feedback
- Compatible with multiple Chainlit versions

Architecture:
User Interface (Chainlit) → FastAPI Backend → ChromaDB → LLM (Groq)

Compatible with Chainlit versions that require:
- Action.payload (newer versions need this for button actions)
- Action.send(for_id=<message_id>) (actions must be attached to specific messages)
"""

import os
import uuid
import httpx  # HTTP client for making requests to our FastAPI backend
import chainlit as cl  # Chainlit framework for building chat interfaces

# Configuration: Get API URL from environment variables with fallback
API = os.getenv("API_URL", "http://127.0.0.1:8000")

# Available LLM models that users can choose from
ALLOWED_MODELS = ["llama3-70b-8192", "mixtral-8x7b-32768"]

def new_chat_uid() -> str:
    """
    Generate a unique identifier for each chat session.
    
    This UUID ensures that each conversation is isolated and documents
    uploaded in one session don't interfere with another session.
    
    Returns:
        str: A unique UUID string for the chat session
    """
    return str(uuid.uuid4())

@cl.on_chat_start
async def on_start():
    """
    Initialize a new chat session when a user connects.
    
    This function runs automatically when someone opens the Chainlit interface.
    It sets up the session, creates UI controls, and prepares the upload functionality.
    
    Key responsibilities:
    1. Create a unique session ID (chat_uid)
    2. Set up user interface controls (if supported by Chainlit version)
    3. Initialize session variables (model, bot name)
    4. Create the document upload button
    """
    # Step 1: Create unique session identifier
    chat_uid = new_chat_uid()
    cl.user_session.set("chat_uid", chat_uid)  # Store in session for later use

    # Step 2: Display connection information to user
    await cl.Message(content=f"Using API_URL: {API}").send()

    # Step 3: Set default configuration values
    model = ALLOWED_MODELS[0]  # Default to first available model
    bot_name = "Assistant"     # Default bot name

    # Step 4: Try to create modern UI controls (sidebar with inputs)
    # This uses newer Chainlit features that may not be available in all versions
    try:
        with cl.ui.sidebar():
            # Create sidebar title
            cl.ui.text("Session Setup", variant="h3")
            
            # Create state variables to track user inputs
            model_state = cl.ui.state(model)      # Tracks selected model
            bot_state = cl.ui.state(bot_name)     # Tracks bot name

            # Callback functions for when user changes inputs
            def on_model_change(value):
                """Update model state when user selects different model"""
                model_state.set(value)

            def on_name_change(value):
                """Update bot name state when user types new name"""
                bot_state.set(value)

            # Create input field for model selection
            cl.ui.input(
                label="Model",
                placeholder=ALLOWED_MODELS[0],
                value=model_state.get(),
                on_change=on_model_change,
            )
            
            # Create input field for bot name customization
            cl.ui.input(
                label="Chatbot name",
                placeholder="Assistant",
                value=bot_state.get(),
                on_change=on_name_change,
            )

            # Save button to apply settings
            def on_save():
                """Save user settings to session when Save button is clicked"""
                cl.user_session.set("model", model_state.get())
                cl.user_session.set("bot_name", bot_state.get())
                # Show success notification
                cl.ui.toast(
                    f"Saved: model={model_state.get()}, bot={bot_state.get()}",
                    variant="success"
                )

            cl.ui.button("Save Settings", on_click=on_save, variant="primary")

        # Store default settings in session
        cl.user_session.set("model", model)
        cl.user_session.set("bot_name", bot_name)

    except Exception:
        # Step 5: Fallback for older Chainlit versions without sidebar support
        # Provide text-based configuration instructions
        await cl.Message(
            content=(
                "Configure your assistant by replying with a line like:\n"
                "bot=Assistant; model=llama3-70b-8192\n"
                "Or just start chatting to use defaults."
            ),
            author="Setup"
        ).send()
        
        # Still store default settings
        cl.user_session.set("model", model)
        cl.user_session.set("bot_name", bot_name)

    # Step 6: Display session information to user
    await cl.Message(content=f"Session created: {chat_uid}").send()

    # Step 7: Create document upload functionality
    # First, create a message that will contain the upload button
    setup_msg = cl.Message(
        content="Optional: Click the button below to upload documents to index for this session."
    )
    await setup_msg.send()

    # Then, create an Action (button) attached to that message
    # This is the fixed version that works with newer Chainlit versions
    await cl.Action(
        name="Upload documents",           # Button text
        payload={"action": "upload"}       # Required by newer Chainlit versions
    ).send(for_id=setup_msg.id)          # Must attach to specific message

@cl.on_message
async def on_message(msg: cl.Message):
    """
    Handle incoming user messages.
    
    This function processes two types of messages:
    1. Configuration commands (e.g., "bot=MyBot; model=llama3-70b-8192")
    2. Regular chat queries that need to be sent to the backend
    
    Args:
        msg: The message object containing user input
    """
    import re
    
    # Step 1: Check if message is a configuration command
    # Pattern matches: "bot=SomeName; model=SomeModel" (flexible spacing)
    config_match = re.search(r"bot\s*=\s*([^;]+);?\s*model\s*=\s*([^\n\r;]+)", msg.content, re.IGNORECASE)
    
    if config_match:
        # Extract bot name and model from the regex groups
        bot_name = config_match.group(1).strip()
        model = config_match.group(2).strip()
        
        # Save to session
        cl.user_session.set("bot_name", bot_name)
        cl.user_session.set("model", model)
        
        # Confirm settings were saved
        await cl.Message(content=f"Saved settings: model={model}, bot={bot_name}").send()
        return  # Don't process as regular chat message

    # Step 2: Get session variables for regular chat processing
    chat_uid = cl.user_session.get("chat_uid")                    # Session ID
    model = cl.user_session.get("model") or ALLOWED_MODELS[0]     # Selected model
    bot_name = cl.user_session.get("bot_name") or "Assistant"     # Bot name

    # Step 3: Validate session exists
    if not chat_uid:
        await cl.Message(content="No active session. Please restart the chat.").send()
        return

    # Step 4: Prepare request payload for FastAPI backend
    payload = {
        "query": msg.content,        # User's question/message
        "model": model,              # Selected LLM model
        "chat_uid": chat_uid,        # Session identifier
        "chatbot_name": bot_name,    # Customized bot name
    }

    # Step 5: Create empty message for streaming response
    # This message will be updated in real-time as tokens arrive
    stream_msg = cl.Message(content="")
    await stream_msg.send()

    try:
        # Step 6: Send request to FastAPI backend and stream response
        async with httpx.AsyncClient(timeout=None) as client:
            # Make streaming POST request to /chat endpoint
            async with client.stream("POST", f"{API}/chat", json=payload) as resp:
                resp.raise_for_status()  # Raise exception for HTTP errors
                
                # Stream each chunk of the response as it arrives
                async for chunk in resp.aiter_text():
                    if chunk:
                        # Add each token to the streaming message
                        await stream_msg.stream_token(chunk)
        
        # Step 7: Finalize the streamed message
        await stream_msg.update()
        
    except Exception as e:
        # Handle any errors during chat processing
        await cl.Message(content=f"Chat failed: {e}").send()

@cl.action_callback("Upload documents")
async def on_upload_action(action: cl.Action):
    """
    Handle document upload action when user clicks the upload button.
    
    This function:
    1. Validates the action and session
    2. Prompts user to select files
    3. Processes uploaded files
    4. Sends files to FastAPI backend for indexing
    5. Provides feedback to user
    
    Args:
        action: The Action object containing button click information
    """
    # Step 1: Handle different Chainlit versions for action data
    # Newer versions use 'payload', older versions use 'value'
    payload = getattr(action, "payload", None) or {}
    if isinstance(payload, dict):
        action_name = payload.get("action")
    else:
        action_name = getattr(action, "value", None)

    # Validate this is the upload action
    if action_name != "upload":
        await cl.Message(content="Unknown action.").send()
        return

    # Step 2: Validate session exists
    chat_uid = cl.user_session.get("chat_uid")
    if not chat_uid:
        await cl.Message(content="No active session. Please restart the chat.").send()
        return

    try:
        # Step 3: Prompt user to select files
        files = await cl.AskFileMessage(
            content="Upload files to index (TXT, MD, CSV, JSON, PDF, DOCX).",
            accept=[
                # Text files
                "text/plain", ".txt", ".md", ".csv", ".json",
                # PDF files
                "application/pdf", ".pdf",
                # Word documents
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx",
                "application/msword", ".doc"
            ],
            max_size_mb=25,    # Maximum file size limit
            max_files=8,       # Maximum number of files
            timeout=600        # 10 minute timeout for file selection
        ).send()
    except Exception as e:
        await cl.Message(content=f"Upload prompt failed: {e}").send()
        return

    # Step 4: Validate files were selected
    if not files:
        await cl.Message(content="No files selected.").send()
        return

    # Step 5: Process files for multipart upload
    multipart_files = []

    async def read_bytes_from_ask_file(f) -> bytes | None:
        """
        Extract file bytes from Chainlit AskFileResponse object.
        
        Different Chainlit versions store file data in different attributes,
        so we try multiple methods to ensure compatibility.
        
        Args:
            f: AskFileResponse object from Chainlit
            
        Returns:
            bytes: File content as bytes, or None if unable to read
        """
        # Method 1: Direct data attribute (most common in newer versions)
        data_bytes = getattr(f, "data", None)
        if isinstance(data_bytes, (bytes, bytearray)) and len(data_bytes) > 0:
            return data_bytes

        # Method 2: Content attribute (some versions use this)
        content_attr = getattr(f, "content", None)
        if isinstance(content_attr, (bytes, bytearray)) and len(content_attr) > 0:
            return content_attr

        # Method 3: File path attribute (when files are saved to temp directory)
        fpath = getattr(f, "path", None)
        if isinstance(fpath, str):
            try:
                with open(fpath, "rb") as fp:
                    data = fp.read()
                if data:
                    return data
            except Exception:
                pass  # Continue to next method if file reading fails

        # Method 4: Async getter method (rare, older versions)
        get_content = getattr(f, "get_content", None)
        if callable(get_content):
            try:
                maybe_bytes = get_content()
                # Handle both sync and async getters
                if hasattr(maybe_bytes, "__await__"):
                    maybe_bytes = await maybe_bytes
                if isinstance(maybe_bytes, (bytes, bytearray)) and len(maybe_bytes) > 0:
                    return maybe_bytes
            except Exception:
                pass

        # If all methods fail, return None
        return None

    # Step 6: Process each uploaded file
    for f in files:
        # Extract file metadata
        filename = getattr(f, "name", None) or "upload"  # Filename with fallback
        content_type = getattr(f, "type", None) or "application/octet-stream"  # MIME type
        
        # Extract file content using our compatibility function
        data_bytes = await read_bytes_from_ask_file(f)

        if not data_bytes:
            # Skip files we couldn't read and notify user
            await cl.Message(content=f"Could not read file bytes for {filename}.").send()
            continue

        # Add to multipart form data for HTTP upload
        # Format: (field_name, (filename, file_content, content_type))
        multipart_files.append(("files", (filename, data_bytes, content_type)))

    # Step 7: Validate we have files to upload
    if not multipart_files:
        await cl.Message(content="No valid files to upload.").send()
        return

    # Step 8: Prepare form data with session ID
    data = {"chat_uid": str(chat_uid)}

    try:
        # Step 9: Send files to FastAPI backend for indexing
        async with httpx.AsyncClient(timeout=120) as client:  # 2 minute timeout
            # POST to /index endpoint with files and form data
            res = await client.post(f"{API}/index", data=data, files=multipart_files)
            res.raise_for_status()  # Raise exception for HTTP errors
            payload = res.json()    # Parse JSON response
        
        # Step 10: Display success message to user
        await cl.Message(content=f"Indexing status: {payload.get('status', 'ok')}").send()
        
    except httpx.HTTPStatusError as e:
        # Handle HTTP errors (4xx, 5xx status codes)
        err_text = ""
        try:
            err_text = e.response.text  # Get error details from response
        except Exception:
            pass
        await cl.Message(content=f"Indexing failed: HTTP {e.response.status_code}. {err_text}").send()
        
    except Exception as e:
        # Handle other errors (network issues, timeouts, etc.)
        await cl.Message(content=f"Indexing failed: {e}").send()

"""
Summary of Key Concepts for Students:

1. SESSION MANAGEMENT:
   - Each user gets a unique chat_uid to isolate their conversation
   - Session variables store user preferences (model, bot name)
   - Sessions persist until browser is closed or page is refreshed

2. STREAMING RESPONSES:
   - Messages are displayed token-by-token as they're generated
   - Provides real-time feedback like ChatGPT
   - Uses HTTP streaming to send partial responses

3. FILE UPLOAD HANDLING:
   - Multiple file formats supported (PDF, DOCX, TXT, etc.)
   - Files are processed and sent to backend for embedding generation
   - Compatibility layer handles different Chainlit versions

4. ERROR HANDLING:
   - Comprehensive try/catch blocks for robust error handling
   - User-friendly error messages for common issues
   - Graceful degradation when features aren't available

5. CHAINLIT COMPATIBILITY:
   - Code works with multiple Chainlit versions
   - Fallback mechanisms for older versions
   - Modern UI features when available

6. COMMUNICATION WITH BACKEND:
   - Uses HTTP requests to communicate with FastAPI
   - JSON payloads for chat requests
   - Multipart form data for file uploads
"""