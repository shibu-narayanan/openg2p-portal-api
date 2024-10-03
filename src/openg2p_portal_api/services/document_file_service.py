import hashlib
import json
import mimetypes
import os
import uuid
import boto3
from fastapi import HTTPException
from openg2p_fastapi_common.service import BaseService
from openg2p_portal_api.models.document_file import DocumentFile  
from openg2p_portal_api.models.orm.document_store_orm import DocumentStoreORM
from openg2p_portal_api.models.orm.document_tag_orm import DocumentTagORM
from slugify import slugify
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from ..models.orm.document_file_orm import DocumentFileORM
from openg2p_fastapi_common.context import dbengine
from sqlalchemy.ext.asyncio import async_sessionmaker

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from botocore.exceptions import ClientError
import logging
_logger = logging.getLogger(__name__)


class DocumentFileService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.async_session_maker = async_sessionmaker(dbengine.get())

        #further user for minio configuration
        self.s3_client = None
        self.bucket_name = None



    class DocumentFileService(BaseService):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.async_session_maker = async_sessionmaker(dbengine.get())

            #further use for minio configuration
            self.s3_client = None
            self.bucket_name = None

    async def upload_document_minio(self,file_obj,file_name: str,backend_id:int):

       
        if file_obj is None  :
            raise ValueError("The file object is empty or not readable.")   
        file_obj.seek(0)
        

        # Pull the config for MinIO 
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(DocumentStoreORM).filter_by(id=backend_id)
            )
            backend = result.scalars().first()
            
            if not backend or not backend.server_env_defaults:
                raise ValueError(f"The backend {backend_id} is invalid or does not exist.")

            # Parse server_env_defaults
            if isinstance(backend.server_env_defaults, str):
                try:
                    backend.server_env_defaults = json.loads(backend.server_env_defaults)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format in server_env_defaults.")

            # Extract MinIO configuration
            endpoint_url = backend.server_env_defaults.get("x_aws_host_env_default")
            aws_access_key = backend.server_env_defaults.get("x_aws_access_key_id_env_default")
            aws_secret_key = backend.server_env_defaults.get("x_aws_secret_access_key_env_default")
            region_name = backend.server_env_defaults.get("x_aws_region_env_default")
            bucket_name = backend.server_env_defaults.get("x_aws_bucket_env_default")

            # Configure S3 client
            self.s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name  
            )
            self.bucket_name = bucket_name

        
        # Upload the file to MinIO
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, file_name)
            _logger.info(f"Successfully uploaded file {file_name} to MinIO")
            return {"message": "File successfully uploaded to MinIO"}
        except ClientError as e:
            _logger.error(f"Error uploading file {file_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            _logger.error(f"Unexpected error while uploading file {file_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))


    async def get_document_by_id(self, document_id: int):
        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(DocumentFileORM).where(DocumentFileORM.id == document_id)
                )
                document = result.scalar_one_or_none()

                if not document:
                    raise Exception("Document not found")

                return DocumentFile.from_orm(document)  
            except SQLAlchemyError as e:
                raise Exception("Error retrieving document: " + str(e))



    async def upload_document(self,id:int, name: str, backend_id: int, data: bytes,company_id:int,file_tag:str):
        async with self.async_session_maker() as session:
            
            if data is None:
                raise HTTPException(status_code=400, detail="Content must not be None.")
            
            filename=name 
            extension = os.path.splitext(name)
            mimetype = mimetypes.guess_type(name)[0] or ""

            checksum = hashlib.sha1(data).hexdigest()
            
            new_file = DocumentFileORM(
            id=id,
            name=name,
            backend_id=backend_id,
            file_size=len(data),
            checksum=checksum,
            filename=filename,
            extension=extension,
            mimetype=mimetype,
            company_id=company_id,
            active=True
            )
            self.extract_filename(new_file)
            self.compute_human_file_size(new_file)
            new_file.slug = self.compute_slug(new_file)
            new_file.relative_path = await self.build_relative_path(new_file, checksum)
            new_file.write_uid = await self.get_tag_id_by_name(file_tag)

            session.add(new_file)
            await session.commit() 
            await session.refresh(new_file) 
            
            return DocumentFile.from_orm(new_file) 
        
  

    # not working properly
    async def get_tag_id_by_name(self, tag_name: str) -> int:
        async with self.async_session_maker() as session:  
            try:
                result = await session.execute(
                    select(DocumentTagORM.create_uid).where(DocumentTagORM.name == tag_name)
                )
                tag_id = result.scalars().first()  
                if tag_id is None:
                    raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found.")
                return tag_id
            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=f"Error retrieving tag: {str(e)}")



    async def build_relative_path(self, document_file: DocumentFileORM, checksum: str) -> str:
        """Build relative path based on filename strategy."""
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(DocumentStoreORM).filter_by(id=document_file.backend_id)
            )
            backend = result.scalars().first()
            
            if not backend or not backend.server_env_defaults:
                raise ValueError(f"The backend {document_file.backend_id} is invalid or does not exist.")

            if isinstance(backend.server_env_defaults, str):
                try:
                    backend.server_env_defaults = json.loads(backend.server_env_defaults)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format in server_env_defaults.")

            filename_strategy = backend.server_env_defaults.get("x_filename_strategy_env_default", "default_strategy")

            if filename_strategy == "hash":
                return f"{checksum[:2]}/{checksum}"
            elif filename_strategy == "name_with_id":
                return document_file.slug
            else:
                raise ValueError(f"Unknown filename strategy: {filename_strategy}")



    def compute_human_file_size(self, document_file: DocumentFileORM):
        """Compute human-readable file size."""
        if document_file.file_size is not None:
            document_file.human_file_size = self.human_size(document_file.file_size)



    def compute_slug(self, document_file: DocumentFileORM) -> str:
        """Generate slug based on filename and ID."""
        if document_file.filename:
            return self.slugify_name_with_id(document_file)


    def human_size(self, size: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    

    def extract_filename(self, document_file: DocumentFileORM):
        """Extract filename and extension from name."""
        if document_file.name:
            document_file.filename, document_file.extension = os.path.splitext(document_file.name)
            document_file.mimetype = mimetypes.guess_type(document_file.name)[0] or ""

    def slugify_name_with_id(self, document_file: DocumentFileORM) -> str:
        """Create slugified name for URL."""
        document_id = document_file.id if document_file.id is not None else str(uuid.uuid4())
        return f"{slugify(f'{document_file.filename}-{document_id}')}{document_file.extension}"
