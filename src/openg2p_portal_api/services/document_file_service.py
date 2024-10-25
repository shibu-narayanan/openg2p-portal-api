import hashlib
import mimetypes
import os

import boto3
from botocore.exceptions import ClientError
from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.errors.http_exceptions import BadRequestError
from openg2p_fastapi_common.service import BaseService
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from openg2p_portal_api.exception import handle_exception
from openg2p_portal_api.models.document_file import DocumentFile
from openg2p_portal_api.utils.file_utils import (
    compute_human_file_size,
    create_or_update_tag,
    extract_filename,
    fullpath,
    get_company_and_backend_id_by_programid,
    get_file_id_by_slug,
    get_s3_backend_config,
    update_slug_relative_path,
)

from ..models.orm.document_file_orm import DocumentFileORM


class DocumentFileService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.async_session_maker = async_sessionmaker(dbengine.get())

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
                handle_exception(e, "Failed to retrieve document by ID")

    async def upload_document(self, file, programid: int, file_tag: str):
        """
        Uploads a document to Amazon S3 or local filesystem and saves its metadata in the database.
        """
        async with self.async_session_maker() as session:
            # Retrieve company and backend IDs
            (
                company_id,
                backend_id,
            ) = await get_company_and_backend_id_by_programid(self, programid)

            # Fetching the backend on the basis of backend_id
            backend = await get_s3_backend_config(self, backend_id)
            # Determine backend type and upload document
            backend_type = backend.server_env_defaults.get("x_backend_type_env_default")

            if backend_type == "amazon_s3" or backend_type == "filesystem":
                name = file.filename
                data = await file.read()
                if data is None:
                    raise BadRequestError(
                        message="Failed to upload document: Content must not be None."
                    ) from None
                # Create or update document tag
                if file_tag:
                    await create_or_update_tag(self, file_tag)

                # Compute file metadata
                checksum = hashlib.sha1(data).hexdigest()
                new_file = DocumentFileORM(
                    name=name,
                    backend_id=backend_id,
                    file_size=len(data),
                    checksum=checksum,
                    filename=name,
                    extension=os.path.splitext(name),
                    mimetype=mimetypes.guess_type(name)[0] or "",
                    company_id=company_id,
                    active=True,
                )
                extract_filename(new_file)
                compute_human_file_size(new_file)
                session.add(new_file)
                await session.commit()
                await session.refresh(new_file)

                # Generate slugified filename
                slugified_filename = slugify(name)
                file_id = await get_file_id_by_slug(self)
                final_filename = f"{slugified_filename}-{file_id}"
                await update_slug_relative_path(self, file_id, final_filename)

                # Upload file to backend storage
                if backend_type == "amazon_s3":
                    return await self.S3_StorageSystem(file, final_filename, backend)
                elif backend_type == "filesystem":
                    full_path = fullpath(final_filename)
                    return await self.file_StorageSystem(full_path, data)

            else:
                raise BadRequestError(
                    message="Backend configuration not belong amazon_s3 or fileStorageSystem "
                ) from None

    async def S3_StorageSystem(self, file: object, file_name: str, backend: object):
        """
        Upload a file to an S3-compatible storage system (e.g., MinIO) using the provided backend configuration.
        """
        file_obj = file.file
        if file_obj is None:
            raise BadRequestError(
                message="The file object is empty or not readable."
            ) from None

        if not hasattr(file_obj, "seek"):
            raise BadRequestError(message="he file object is not seekable.") from None
        file_obj.seek(0)

        # Retrieve S3 configuration
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
            # Initialize S3 client
            s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name,
            )
            bucket_name = bucket_name
            # Upload file to S3
            s3_client.upload_fileobj(file_obj, bucket_name, file_name)
        except ClientError as e:
            handle_exception(e, "Client error occurred")
        except Exception as e:
            handle_exception(e, f"Unexpected error while uploading file {file_name}")
        return {"Message": "File Upload on s3 Successfully "}

    async def file_StorageSystem(self, full_path: str, data: bytes):
        """
        Add a file at the specified relative path in the local filesystem.
        """
        try:
            # Ensure directory exists
            dirname = os.path.dirname(full_path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            # Write file data
            with open(full_path, "wb") as my_file:
                my_file.write(data)
        except OSError as e:
            handle_exception(e, "Error creating directory or writing file")
        except TypeError as e:
            handle_exception(e, "Invalid data type")
        except Exception as e:
            handle_exception(e, "Unexpected error while writing file")
        return {"Message": "File Upload Successfully in fileStorage "}
