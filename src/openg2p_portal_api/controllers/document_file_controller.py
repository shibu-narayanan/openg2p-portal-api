from fastapi import APIRouter, HTTPException, UploadFile, File
from openg2p_fastapi_common.controller import BaseController
from openg2p_portal_api.models.document_file import DocumentFile 
from ..services.document_file_service import DocumentFileService  
import logging
_logger = logging.getLogger(__name__)

from ..config import Settings
_config = Settings.get_config()

class DocumentFileController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._file_service = DocumentFileService.get_component()

        self.router = APIRouter()
        self.router.tags += ["DocumentStore"]

        self.router.add_api_route(
            "/uploadDocument",
            self.upload_document,
            responses={200: {"model": DocumentFile}},
            methods=["POST"],
        )

        self.router.add_api_route(
            "/getDocument/{document_id}",
            self.get_document_by_id,
            responses={200: {"model": DocumentFile}},
            methods=["GET"],
        )

    @property
    def file_service(self):
        if not self._file_service:
            self._file_service = DocumentFileService.get_component()
        return self._file_service


    async def upload_document(
        self,
        # file_id: int,
        # name: str,
        file_tag: str,
        storage_id: int,
        file: UploadFile = File(...),
        company_id: int = None,
    ):
        try:
            # File upload on Odoo
            file_content = await file.read()
            await self.file_service.upload_document(
                # id=file_id,
                # name=name,
                name = file.filename,
                backend_id=storage_id,
                data=file_content,
                company_id=company_id,
                file_tag=file_tag
            )

            # File upload on MinIO
            await self.file_service.upload_document_minio(
                file.file,
                file_name = file.filename,
                backend_id = storage_id,
                # file_id=file_id,
            )

            return {"message": "File uploaded successfully on MinIO and Odoo", "file_name": file.filename}
        
        except Exception as e:
            _logger.error("Error uploading document: %s", str(e))
            raise HTTPException(status_code=400, detail=str(e))


    async def get_document_by_id(self, document_id: int):
        try:
            document = await self.file_service.get_document_by_id(document_id)
            return document
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

   