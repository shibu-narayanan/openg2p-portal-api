import hashlib
import json
import mimetypes
import os
import re

import boto3
from botocore.exceptions import ClientError
from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.errors.http_exceptions import BadRequestError
from openg2p_fastapi_common.service import BaseService
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from openg2p_portal_api.models.document_file import DocumentFile
from openg2p_portal_api.models.orm.document_store_orm import DocumentStoreORM
from openg2p_portal_api.models.orm.document_tag_orm import DocumentTagORM
from openg2p_portal_api.models.orm.program_orm import ProgramORM

from ..config import Settings
from ..models.orm.document_file_orm import DocumentFileORM

_config = Settings.get_config()


class DocumentFileService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.async_session_maker = async_sessionmaker(dbengine.get())
        self.filestore_path = _config.filestore_path

    async def get_document_by_id(self, document_id: int):
        """
        Retrieve a document from the database by its ID.
        """
        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(DocumentFileORM).where(DocumentFileORM.id == document_id)
                )
                document = result.scalar_one_or_none()

                if not document:
                    raise BadRequestError(message="Document not found") from None

                return DocumentFile.from_orm(document)
            except SQLAlchemyError as e:
                raise BadRequestError(
                    message="Failed to retrieve document by ID: " + str(e)
                ) from None

    async def upload_document(self, file, programid: int, file_tag: str):
        """
        Upload a document associated with a specific program ID.

        This method retrieves the backend configuration using the given program ID and validates its
        existence. It then uploads the document to the designated storage backend (either Amazon S3
        or filesystem) by calling the appropriate upload method. If the backend type is unsupported
        or if any errors occur during the process, a BadRequestError is raised.
        """
        async with self.async_session_maker() as session:
            try:
                (
                    company_id,
                    backend_id,
                ) = await self.get_company_and_backend_id_by_programid(programid)

                result = await session.execute(
                    select(DocumentStoreORM).filter_by(id=backend_id)
                )
                backend = result.scalars().first()

                if not backend or not backend.server_env_defaults:
                    raise BadRequestError(
                        message=f"The backend {backend_id} is invalid or does not exist."
                    ) from None

                if isinstance(backend.server_env_defaults, str):
                    backend.server_env_defaults = json.loads(
                        backend.server_env_defaults
                    )

                backend_type = backend.server_env_defaults.get(
                    "x_backend_type_env_default"
                )
                if backend_type == "amazon_s3" or backend_type == "filesystem":
                    return_message = await self.upload_document_odoo(
                        file, file_tag, backend_id, company_id, backend_type, backend
                    )
                else:
                    raise BadRequestError(
                        message="Backend type not configured for the given programid."
                    ) from None
            except SQLAlchemyError as e:
                raise BadRequestError(message=f"Database error: {str(e)}") from None
            except Exception as e:
                raise BadRequestError(message=f"Unexpected error: {str(e)}") from None
        return return_message

    async def upload_document_odoo(
        self,
        file: object,
        file_tag: str,
        backend_id: int,
        company_id: int,
        backend_type: str,
        backend: object,
    ):
        """
        Upload a document and save its metadata to the database.
        Parameters:
            file (object): The file object to be uploaded.
            file_tag (str): An optional tag for categorizing the document.
            backend_id (int): The identifier for the backend storage.
            company_id (int): The identifier for the company associated with the document.
            backend_type (str): The type of backend storage (e.g., 'amazon_s3' or 'filesystem').
            backend (object): The backend configuration object used for the upload process.
        """

        async with self.async_session_maker() as session:
            name = file.filename
            data = await file.read()
            if data is None:
                raise BadRequestError(
                    message="Failed to upload document: Content must not be None."
                ) from None

            if file_tag:
                await self.create_or_update_tag(file_tag)

            filename = name
            extension = os.path.splitext(name)
            mimetype = mimetypes.guess_type(name)[0] or ""
            checksum = hashlib.sha1(data).hexdigest()

            new_file = DocumentFileORM(
                name=name,
                backend_id=backend_id,
                file_size=len(data),
                checksum=checksum,
                filename=filename,
                extension=extension,
                mimetype=mimetype,
                company_id=company_id,
                active=True,
            )
            self.extract_filename(new_file)
            self.compute_human_file_size(new_file)
            session.add(new_file)
            await session.commit()
            await session.refresh(new_file)

            slugified_filename = slugify(name)
            file_id = await self.get_file_id_by_slug()
            final_filename = f"{slugified_filename}-{file_id}"
            await self.update_slug_relative_path(file_id, final_filename)

            if backend_type == "amazon_s3":
                return await self.S3_StorageSystem(file, final_filename, backend)

            elif backend_type == "filesystem":
                full_path = await self._fullpath(final_filename)
                return await self.fileStorageSystem(final_filename, full_path, data)

    async def S3_StorageSystem(self, file: object, file_name: str, backend: object):
        """
        This method uploads a provided file to an S3-compatible storage system (MinIO) using the backend configuration.
        Parameters:
            file (object): The file object to be uploaded.
            file_name (str): The name to be assigned to the uploaded file in the storage.
            backend (object): The backend configuration object containing the necessary credentials and settings for S3.
        """
        file_obj = file.file
        if file_obj is None:
            raise BadRequestError(
                message="The file object is empty or not readable."
            ) from None

        if not hasattr(file_obj, "seek"):
            raise BadRequestError(message="he file object is not seekable.") from None
        file_obj.seek(0)

        endpoint_url = backend.server_env_defaults.get("x_aws_host_env_default")
        aws_access_key = backend.server_env_defaults.get(
            "x_aws_access_key_id_env_default"
        )
        aws_secret_key = backend.server_env_defaults.get(
            "x_aws_secret_access_key_env_default"
        )
        region_name = backend.server_env_defaults.get("x_aws_region_env_default")
        bucket_name = backend.server_env_defaults.get("x_aws_bucket_env_default")
        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name,
            )
            self.bucket_name = bucket_name
        except Exception as e:
            raise BadRequestError(
                message=f"Failed to initialize S3 client: {str(e)}"
            ) from None

        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, file_name)
        except ClientError as e:
            raise BadRequestError(message=f"Client error occurred: {str(e)}") from None
        except Exception as e:
            raise BadRequestError(
                message=f"Unexpected error while uploading file {file_name}: {e}"
            ) from None
        return {"Message": "File Upload on s3 Successfully "}

    async def fileStorageSystem(
        self, relative_path: str, full_path: str, data: bytes
    ) -> None:
        """
        Add a file at the specified relative path in the local filesystem.
        Parameters:
            relative_path (str): The relative path where the file should be stored.
            full_path (str): The complete path (including filename) where the file will be saved.
            data (bytes): The binary content of the file to be written.
        """
        dirname = os.path.dirname(full_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        with open(full_path, "wb") as my_file:
            my_file.write(data)
        return {"Message": "File Upload Successfully in fileStorage "}

    # _is_safe_path and _fullpath are helper methods for fileStorageSystem
    async def is_safe_path(self, basedir: str, path: str) -> bool:
        """Check if the path is within the base directory."""
        return os.path.realpath(path).startswith(basedir)

    async def _basedir(self) -> str:
        """Return the base directory for file storage."""
        # TODO:Retrieve the filestore_path from the ir.attachment model in Odoo.
        base_directory = os.path.join(self.filestore_path, "storage")
        return base_directory

    async def _fullpath(self, relative_path: str) -> str:
        """Build the full path for the file and ensure it's safe."""
        base_dir = await self._basedir()
        full_path = os.path.join(base_dir, relative_path)
        if not await self.is_safe_path(base_dir, full_path):
            raise BadRequestError(
                message=f"Access to {full_path} is forbidden."
            ) from None
        return full_path

    # Below are all helper methods for the upload docs in Odoo
    async def create_or_update_tag(self, tag_name: str):
        """
        Checks for an existing tag; updates it if found, or creates a new tag if not.
        """
        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(DocumentTagORM).where(DocumentTagORM.name == tag_name)
                )
                existing_tag = result.scalars().first()

                if existing_tag:
                    existing_tag.name = tag_name
                    await session.commit()
                    await session.refresh(existing_tag)
                else:
                    new_tag = DocumentTagORM(name=tag_name)
                    session.add(new_tag)
                    await session.commit()
                    await session.refresh(new_tag)

            except SQLAlchemyError as e:
                await session.rollback()
                raise BadRequestError(
                    message="Error creating or updating tag: " + str(e)
                ) from None

    async def get_company_and_backend_id_by_programid(self, programid: int):
        """
        Fetch the company_id and backend_id from the ProgramORM using the provided programid.
        """
        async with self.async_session_maker() as session:
            result = await session.execute(select(ProgramORM).filter_by(id=programid))
            program = result.scalars().first()
            if program:
                return program.company_id, program.supporting_documents_store
            else:
                return None, None

    async def get_file_id_by_slug(self):
        """
        Update the document's slug and relative path in the database after it is uploaded.
        """
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(DocumentFileORM)
                .where(DocumentFileORM.slug.is_(None))
                .order_by(DocumentFileORM.id.desc())
                .limit(1)
            )
            document_file = result.scalars().first()
            if document_file:
                return document_file.id
            else:
                return None

    async def update_slug_relative_path(self, file_id: int, slug: str):
        """
        Updates the slug and relative path of a document file identified by its ID.
        """
        async with self.async_session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(DocumentFileORM).where(DocumentFileORM.id == file_id)
                )
                document_file = result.scalars().first()
                if document_file:
                    document_file.slug = slug
                    document_file.relative_path = slug
                    await session.commit()
                else:
                    raise BadRequestError(
                        message=f"Document file with ID {file_id} not found."
                    ) from None

    def slugify(value: str) -> str:
        """
        Convert a string to a slug: lowercase, replace spaces with dashes, and remove non-alphanumeric characters.
        """
        value = value.lower()
        value = re.sub(r"\s+", "-", value)
        value = re.sub(r"[^a-z0-9-]", "", value)
        value = value.strip("-")
        return value

    def compute_human_file_size(self, document_file: DocumentFileORM):
        """Compute human-readable file size."""
        if document_file.file_size is not None:
            document_file.human_file_size = self.human_size(document_file.file_size)

    def human_size(self, size: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def extract_filename(self, document_file: DocumentFileORM):
        """Extract filename and extension from name."""
        if document_file.name:
            document_file.filename, document_file.extension = os.path.splitext(
                document_file.name
            )
            document_file.mimetype = mimetypes.guess_type(document_file.name)[0] or ""
