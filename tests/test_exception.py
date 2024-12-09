import pytest
from openg2p_fastapi_common.errors.http_exceptions import BadRequestError
from openg2p_portal_api.exception import handle_exception


class TestExceptionHandler:
    @pytest.mark.parametrize(
        "error, expected_message",
        [
            (ValueError("Test error message"), "Error: Test error message"),
            (RuntimeError("Something went wrong"), "Error: Something went wrong"),
            (Exception(), "Error: "),
        ],
    )
    def test_handle_exception(self, error, expected_message):
        with pytest.raises(BadRequestError) as exc_info:
            handle_exception(error)

        assert expected_message in str(
            exc_info.value.detail
        ), f"Expected '{expected_message}' in error detail, but got '{exc_info.value.detail}'"

    def test_handle_exception_with_custom_prefix(self):
        test_error = RuntimeError("Something went wrong")
        custom_prefix = "Custom Error"
        expected_message = "Custom Error: Something went wrong"

        with pytest.raises(BadRequestError) as exc_info:
            handle_exception(test_error, message_prefix=custom_prefix)

        assert expected_message in str(
            exc_info.value.detail
        ), f"Expected '{expected_message}' in error detail, but got '{exc_info.value.detail}'"
