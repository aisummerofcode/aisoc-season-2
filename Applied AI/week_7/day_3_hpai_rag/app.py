from src.utils.constants import *
from src.utils.data import *

app = FastAPI()

@app.get('/health')
async def health_check():
    return JSONResponse(
        content={
            "application": "AISOC RAG App v1",
            "version": "1.0.0",
            "message": "API endpoint working!"
        }
    )

@app.post("/index")
async def process(
    project_id: str = Form(...),
    files: List[UploadFile] = None,
    # urls: List[str] = None
): 

    try:
        logger.info(f"Starting upload process for project {project_id}")
        output = await DataHandler().upload_files(files, project_id)
        return output
        
    except Exception as e:
        exception = traceback.format_exc()
        message = f"Could not proceed to indexing due to exception:"
        logger.info(f"{message}: {exception}")
        return JSONResponse(
            content={"status": f"{message}: {e}"},
            status_code=500
        )


if __name__=="__main__":
    import uvicorn
    logger.info("Starting AISOC Chat Engine...")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)


