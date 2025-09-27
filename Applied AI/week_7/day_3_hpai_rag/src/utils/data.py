import os
from src.utils.constants import *

class DataHandler:

    data_dir = env_config.data_dir + "/projects"

    ALLOWED_FILES: List = [
        "txt", "csv", "htm", "html", "pdf", "json", "doc", "docx", "pptx"
    ]

    def is_allowed_file(self, filename:str) -> bool:
        return "." in filename and filename.rsplit(".",1)[-1].lower() in self.ALLOWED_FILES

    def run_file_checks(self, files: List[UploadFile]):

        if not files:
            message = f"No file found"
            logger.error(message)
            return JSONResponse(
                content={
                    "status": message},
                status_code=400
            )
        
        for file in files:
            filename = file.filename
            if not file or filename == "":
                message = f"No selected file"
                logger.error(message)
                return JSONResponse(
                    content ={
                        "status": message
                    },
                    status_code=400
                )
            
            if not self.is_allowed_file(filename):
                message = f"File format {filename.rsplit('.',1)[-1].lower()} not supported. Use any of {self.ALLOWED_FILES}"
                logger.warning(message)
                return JSONResponse(
                    content={"status": message},
                    status_code=415
                )
        
        return JSONResponse(
            content={"status": "success"},
            status_code=200
        )

    async def upload_files(
        self,
        files: List[UploadFile],
        project_id
    ):
        file_checks = self.run_file_checks(files)
        if file_checks.status_code==200:
            filename = ""
            try:
                for file in files:
                    filename = file.filename

                    # create project dir with project_id if not exist
                    project_dir = os.path.join(self.data_dir, project_id)
                    if project_dir and not os.path.exists(project_dir):
                        os.makedirs(project_dir, exist_ok=True)

                    filepath = os.path.join(project_dir, filename)
                    file_obj = await file.read()

                    with open(filepath, "wb") as buffer:
                        buffer.write(file_obj)
        
                message = f"Files uploaded successfully."
                logger.info(message)
                return JSONResponse(
                    content={"status": message},
                    status_code=200
                )
            
            except Exception as e:
                message = f"An error occured while trying to upload the file, {filename}: {e}"
                logger.error(message)
                raise UploadError(message)
            
        raise FileCheckError(file_checks["status"])
