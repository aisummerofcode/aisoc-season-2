from src.utils.constants import *
from src.utils import DataHandler, EmbeddingHandler

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
    tenant_id: str = Form(...),
    project_id: str = Form(...),
    files: List[UploadFile] = None,
    # urls: List[str] = None
): 

    try:
        logger.info(f"\nStarting upload process for project {project_id}")
        await DataHandler().upload_files(files, project_id)
        # return output
        
    except Exception as e:
        exception = traceback.format_exc()
        message = f"Could not proceed to indexing due to exception:"
        logger.info(f"{message}: {exception}")
        return JSONResponse(
            content={"status": f"{message}: {e}"},
            status_code=500
        )
        
    try:
        data_path = f"{env_config.data_dir}/projects/{project_id}"
        documents = SimpleDirectoryReader(data_path).load_data()
        await EmbeddingHandler().generate_and_store_embeddings(project_id, tenant_id, documents)
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
                "status": f"An error occured during indexing: {str(e)}. \
                    Check the system logs for more information.",
            },
            status_code=400
        )

if __name__=="__main__":
    import uvicorn
    logger.info("Starting AISOC Chat Engine...")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)


