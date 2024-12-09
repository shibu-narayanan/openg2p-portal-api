from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from openg2p_fastapi_common.errors.http_exceptions import BadRequestError
from openg2p_portal_api.models.document_file import DocumentFile
from openg2p_portal_api.models.orm.document_file_orm import DocumentFileORM
from openg2p_portal_api.models.orm.document_store_orm import DocumentStoreORM
from openg2p_portal_api.models.orm.document_tag_orm import DocumentTagORM
from openg2p_portal_api.models.orm.program_orm import ProgramORM
from openg2p_portal_api.services.document_file_service import DocumentFileService
from sqlalchemy.ext.asyncio import AsyncSession

TEST_CONSTANTS = {
    "PROGRAM_ID": 1,
    "FILE_TAG": "test_tag",
    "DOCUMENT_NAME": "test.pdf",
    "DOCUMENT_ID": 1,
    "DOCUMENT_NOT_FOUND_ID": 999,
    "SUCCESS_MESSAGE": "File uploaded successfully.",
    "FILESYSTEM_UNSUPPORTED_MESSAGE": "Uploading files via the filesystem is currently not supported.",
    "INVALID_BACKEND_MESSAGE": "Backend type should be either amazon_s3 or filesystem.",
    "EMPTY_CONTENT_ERROR": "Failed to upload document: Content must not be None.",
}


@pytest.fixture
def document_service():
    service = DocumentFileService()
    mock_session = AsyncMock(spec=AsyncSession)
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = mock_session
    service.async_session_maker = MagicMock(return_value=context_manager)
    return service


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_file():
    file = MagicMock(spec=UploadFile)
    file.filename = TEST_CONSTANTS["DOCUMENT_NAME"]
    file.file = MagicMock()
    file.file.seek = MagicMock()
    return file


@pytest.fixture
def mock_program():
    return ProgramORM(
        id=TEST_CONSTANTS["PROGRAM_ID"], company_id=1, supporting_documents_store=1
    )


@pytest.fixture
def mock_backend_s3():
    return DocumentStoreORM(
        id=1, server_env_defaults={"x_backend_type_env_default": "amazon_s3"}
    )


@pytest.fixture
def mock_backend_filesystem():
    return DocumentStoreORM(
        id=1, server_env_defaults={"x_backend_type_env_default": "filesystem"}
    )


class TestDocumentFileService:
    @pytest.mark.asyncio
    async def test_get_document_by_id_success(self, document_service, mock_session):
        mock_document = DocumentFileORM(
            name=TEST_CONSTANTS["DOCUMENT_NAME"],
            backend_id=1,
            file_size=1000,
            checksum="abc123",
            company_id=1,
            active=True,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_document
        mock_session.execute.return_value = mock_result
        document_service.async_session_maker.return_value.__aenter__.return_value = (
            mock_session
        )

        result = await document_service.get_document_by_id(
            TEST_CONSTANTS["DOCUMENT_ID"]
        )

        assert isinstance(
            result, DocumentFile
        ), "Result should be an instance of DocumentFile"
        assert (
            result.name == mock_document.name
        ), f"Document name should be {mock_document.name}"

    @pytest.mark.asyncio
    async def test_get_document_by_id_not_found(self, document_service, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        document_service.async_session_maker.return_value.__aenter__.return_value = (
            mock_session
        )

        with pytest.raises(BadRequestError) as exc_info:
            await document_service.get_document_by_id(
                TEST_CONSTANTS["DOCUMENT_NOT_FOUND_ID"]
            )
        assert (
            str(exc_info.value.detail) == "Document not found"
        ), "Exception detail should indicate document not found"

    @pytest.mark.asyncio
    async def test_upload_s3_success(
        self, document_service, mock_session, mock_file, mock_program, mock_backend_s3
    ):
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.first.side_effect = [
            mock_program,
            mock_backend_s3,
        ]
        mock_session.execute.return_value = mock_result

        document_service.async_session_maker.return_value.__aenter__.return_value = (
            mock_session
        )

        with patch("boto3.client") as mock_boto3:
            mock_s3_client = MagicMock()
            mock_boto3.return_value = mock_s3_client

            result = await document_service.s3_storage_system(
                mock_file, TEST_CONSTANTS["PROGRAM_ID"], mock_backend_s3
            )

            assert (
                result["message"] == TEST_CONSTANTS["SUCCESS_MESSAGE"]
            ), "S3 upload should return success message"
            mock_s3_client.upload_fileobj.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_document_filesystem(
        self,
        document_service,
        mock_session,
        mock_file,
        mock_program,
        mock_backend_filesystem,
    ):
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.first.side_effect = [
            mock_program,
            mock_backend_filesystem,
        ]
        mock_session.execute.return_value = mock_result

        document_service.async_session_maker.return_value.__aenter__.return_value = (
            mock_session
        )

        result = await document_service.upload_document(
            mock_file, TEST_CONSTANTS["PROGRAM_ID"], TEST_CONSTANTS["FILE_TAG"]
        )

        assert (
            result["message"] == TEST_CONSTANTS["FILESYSTEM_UNSUPPORTED_MESSAGE"]
        ), "Filesystem upload should return unsupported message"

    @pytest.mark.asyncio
    async def test_upload_document_s3(
        self, document_service, mock_session, mock_file, mock_program, mock_backend_s3
    ):
        mock_tag = DocumentTagORM(name=TEST_CONSTANTS["FILE_TAG"])
        mock_document = DocumentFileORM(
            name=TEST_CONSTANTS["DOCUMENT_NAME"],
            backend_id=1,
            file_size=1000,
            checksum="abc123",
            company_id=1,
            active=True,
        )

        mock_session.execute.side_effect = [
            AsyncMock(
                scalars=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=mock_program))
                )
            ),
            AsyncMock(
                scalars=MagicMock(
                    return_value=MagicMock(
                        first=MagicMock(return_value=mock_backend_s3)
                    )
                )
            ),
            AsyncMock(
                scalars=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=None))
                )
            ),
            AsyncMock(
                scalars=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=mock_tag))
                )
            ),
            AsyncMock(
                scalars=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=mock_document))
                )
            ),
            AsyncMock(),
        ]

        document_service.async_session_maker.return_value.__aenter__.return_value = (
            mock_session
        )
        mock_file.read = AsyncMock(return_value=b"test content")

        with patch.object(document_service, "s3_storage_system") as mock_s3_storage:
            mock_s3_storage.return_value = {
                "message": TEST_CONSTANTS["SUCCESS_MESSAGE"]
            }
            result = await document_service.upload_document(
                mock_file, TEST_CONSTANTS["PROGRAM_ID"], TEST_CONSTANTS["FILE_TAG"]
            )

            assert (
                result["message"] == TEST_CONSTANTS["SUCCESS_MESSAGE"]
            ), "S3 upload should return success message"
            mock_s3_storage.assert_called_once_with(
                mock_file, str(f"test-pdf-{mock_document.id}"), mock_backend_s3
            )
            assert (
                mock_session.add.call_count == 2
            ), "Two objects should be added to the session"

    @pytest.mark.asyncio
    async def test_upload_document_empty_content(
        self, document_service, mock_session, mock_file, mock_program, mock_backend_s3
    ):
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.first.side_effect = [
            mock_program,
            mock_backend_s3,
        ]
        mock_session.execute.return_value = mock_result

        document_service.async_session_maker.return_value.__aenter__.return_value = (
            mock_session
        )
        mock_file.read = AsyncMock(return_value=None)

        with pytest.raises(BadRequestError) as exc_info:
            await document_service.upload_document(
                mock_file, TEST_CONSTANTS["PROGRAM_ID"], TEST_CONSTANTS["FILE_TAG"]
            )
        assert (
            str(exc_info.value.detail) == TEST_CONSTANTS["EMPTY_CONTENT_ERROR"]
        ), "Exception detail should indicate content must not be None"

    @pytest.mark.asyncio
    async def test_upload_document_invalid_backend(
        self, document_service, mock_session, mock_file, mock_program
    ):
        mock_backend_invalid = DocumentStoreORM(
            id=1, server_env_defaults={"x_backend_type_env_default": "invalid_backend"}
        )

        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.first.side_effect = [
            mock_program,
            mock_backend_invalid,
        ]
        mock_session.execute.return_value = mock_result

        document_service.async_session_maker.return_value.__aenter__.return_value = (
            mock_session
        )

        result = await document_service.upload_document(
            mock_file, TEST_CONSTANTS["PROGRAM_ID"], TEST_CONSTANTS["FILE_TAG"]
        )

        assert (
            result["message"] == TEST_CONSTANTS["INVALID_BACKEND_MESSAGE"]
        ), "Invalid backend should return appropriate error message"
