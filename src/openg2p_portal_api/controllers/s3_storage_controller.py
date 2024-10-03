from fastapi.responses import JSONResponse
from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError
from openg2p_portal_api.services.document_file_service import DocumentFileService

from ..config import Settings
from ..dependencies import JwtBearerAuth
from fastapi import APIRouter, File, UploadFile, HTTPException
_config = Settings.get_config()


class S3Controller(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._file_service = DocumentFileService.get_component()
        self.router = APIRouter()
        self.router.tags += ["S3 Storage"]

        
        self.router.add_api_route(
            "/upload/file",
            self.add_file,
            response_class=JSONResponse,
            methods=["POST"],
        )

    @property
    def file_service(self):
        if not self._file_service:
            self._file_service = DocumentFileService.get_component()
        return self._file_service

    

    async def add_file(self, storage_id:int,file: UploadFile = File(...),):
        """Endpoint for uploading files to MinIO."""
        if not file:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if file.filename == '':
            raise HTTPException(status_code=400, detail="No file selected")
        try:
            await self.file_service.upload_document_minio(file.file, file.filename,backend_id=storage_id)
            

            return {"message": "File uploaded successfully on MinIO", "file_name": file.filename}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
