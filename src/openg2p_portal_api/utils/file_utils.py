import json
import mimetypes
import os

from openg2p_fastapi_common.errors.http_exceptions import BadRequestError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from openg2p_portal_api.exception import handle_exception
from openg2p_portal_api.models.orm.document_file_orm import DocumentFileORM
from openg2p_portal_api.models.orm.document_store_orm import DocumentStoreORM
from openg2p_portal_api.models.orm.document_tag_orm import DocumentTagORM
from openg2p_portal_api.models.orm.program_orm import ProgramORM
from openg2p_portal_api.utils.odoo_server_utils import get_odoo_connection

# Methods: Below are used for managing file storage in the local environment.
# - fullpath
# - is_safe_path
# - basedir


def fullpath(relative_path: str) -> str:
    """
    Build the full path for the file and ensure it's safe.
    """
    base_dir = basedir()
    print(base_dir)
    full_path = os.path.join(base_dir, relative_path)
    if not is_safe_path(base_dir, full_path):
        raise BadRequestError(message=f"Access to {full_path} is forbidden.") from None
    return full_path


def is_safe_path(basedir: str, path: str) -> bool:
    """Check if the path is within the base directory."""
    return os.path.realpath(path).startswith(basedir)


def basedir() -> str:
    """
    Get base directory for file storage.
    """

    try:
        models, db, uid, password = get_odoo_connection()
        filestore_path = models.execute_kw(
            db, uid, password, "ir.attachment", "get_filestore_path", []
        )
        return os.path.join(filestore_path, "storage")
    except Exception as e:
        handle_exception(e, "Error retrieving base directory")


# Methods below are used for uploading documents to Odoo and S3:
# - get_s3_backend_config
# - create_or_update_tag
# - get_company_and_backend_id_by_programid
# - get_file_id_by_slug
# - update_slug_relative_path
# - compute_human_file_size
# - human_size
# - extract_filename


async def get_s3_backend_config(self, backend_id: int):
    """
    Retriving the backend config for s3 on the basis of backend_id
    """
    async with self.async_session_maker() as session:
        result = await session.execute(
            select(DocumentStoreORM).filter_by(id=backend_id)
        )
        backend = result.scalars().first()

        # Validate backend configuration
        if not backend or not backend.server_env_defaults:
            raise BadRequestError(
                message=f"The backend {backend_id} is invalid or does not exist."
            ) from None

        # Parse backend configuration
        if isinstance(backend.server_env_defaults, str):
            backend.server_env_defaults = json.loads(backend.server_env_defaults)
        return backend


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
            handle_exception(e, "Error creating or updating tag")


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
                handle_exception(
                    Exception(f"Document file with ID {file_id} not found.")
                )


def compute_human_file_size(document_file: DocumentFileORM):
    """Compute human-readable file size."""
    if document_file.file_size is not None:
        document_file.human_file_size = human_size(document_file.file_size)


def human_size(size: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def extract_filename(document_file: DocumentFileORM):
    """Extract filename and extension from name."""
    if document_file.name:
        document_file.filename, document_file.extension = os.path.splitext(
            document_file.name
        )
        document_file.mimetype = mimetypes.guess_type(document_file.name)[0] or ""
