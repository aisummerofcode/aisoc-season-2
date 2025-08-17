from src.helpers import *

app = FastAPI()

@app.get('/health')
async def health_check():
    return JSONResponse(
        content={
            "application": "AISOC Chat Engine v1",
            "version": "1.0.0",
            "message": "API endpoint working!"
        }
    )

@app.post("/index")
async def process(
    chat_uid: str = Form(...),
    files: List[UploadFile] = None,
    # urls: List[str] = None
): 

    # try:
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            await upload_files(files, temp_dir)
        except Exception as e:
            exception = traceback.format_exc()
            message = f"Could not proceed to indexing due to exception:"
            logger.info(f"{message}: {exception}")
            return JSONResponse(
                content={"status": f"{message}: {e}"},
                status_code=500
            )
        
        try:
            documents = SimpleDirectoryReader(temp_dir).load_data()
            await generate_and_store_embeddings(chat_uid, documents)
            message = "Embeddings generated and stored successfully."
        
            return JSONResponse(
                content={"status": message},
                status_code=200
            )
        except Exception as e:
            exception = traceback.format_exc()
            logger.error(exception)
            return JSONResponse(
                content={
                    "status": f"An error occured during indexing: {str(e)}. Check the system logs for more information.",
                },
                status_code=400
            )

if __name__=="__main__":
    import uvicorn
    print("Starting AISOC Chat Engine...")
    uvicorn.run(app, host="0.0.0.0", reload=True)
