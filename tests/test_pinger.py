import os
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from app.schemas.monitor import AssertionOperator, AssertionSource
from app.worker.pinger import HttpPinger, PingResult


class TestHttpPinger:
    """Test suite for HttpPinger class."""

    def test_init_default_timeout(self):
        """Test pinger initialization with default timeout."""
        pinger = HttpPinger()
        assert pinger.timeout == 10

    def test_init_custom_timeout(self):
        """Test pinger initialization with custom timeout."""
        pinger = HttpPinger(timeout_seconds=30)
        assert pinger.timeout == 30

    def test_extract_actual_value_status_code(self):
        """Test extracting status code from response."""
        pinger = HttpPinger()
        response = Mock()
        response.status_code = 200

        result = pinger._extract_actual_value(
            AssertionSource.STATUS_CODE, response, 150, None
        )

        assert result == 200

    def test_extract_actual_value_response_time(self):
        """Test extracting response time."""
        pinger = HttpPinger()
        response = Mock()

        result = pinger._extract_actual_value(
            AssertionSource.RESPONSE_TIME, response, 150, None
        )

        assert result == 150

    def test_extract_actual_value_header_with_property(self):
        """Test extracting header value with property name."""
        pinger = HttpPinger()
        response = Mock()
        response.headers = {"Content-Type": "application/json"}

        result = pinger._extract_actual_value(
            AssertionSource.HEADER, response, 150, "Content-Type"
        )

        assert result == "application/json"

    def test_extract_actual_value_header_without_property(self):
        """Test extracting header value without property name raises error."""
        pinger = HttpPinger()
        response = Mock()

        with pytest.raises(
            ValueError, match="Header assertions require a property name"
        ):
            pinger._extract_actual_value(AssertionSource.HEADER, response, 150, None)

    def test_extract_actual_value_body(self):
        """Test extracting response body."""
        pinger = HttpPinger()
        response = Mock()
        response.text = '{"status": "ok"}'

        result = pinger._extract_actual_value(AssertionSource.BODY, response, 150, None)

        assert result == '{"status": "ok"}'

    def test_extract_actual_value_unknown_source(self):
        """Test extracting unknown source raises error."""
        pinger = HttpPinger()
        response = Mock()

        with pytest.raises(ValueError, match="Unknown assertion source"):
            pinger._extract_actual_value("unknown_source", response, 150, None)

    def test_compare_values_equals_success(self):
        """Test EQUALS operator success."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.EQUALS, 200, 200)

        assert success is True
        assert error == ""

    def test_compare_values_equals_failure(self):
        """Test EQUALS operator failure."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.EQUALS, 404, 200)

        assert success is False
        assert "Expected 200, got 404" in error

    def test_compare_values_not_equals_success(self):
        """Test NOT_EQUALS operator success."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.NOT_EQUALS, 404, 200)

        assert success is True
        assert error == ""

    def test_compare_values_not_equals_failure(self):
        """Test NOT_EQUALS operator failure."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.NOT_EQUALS, 200, 200)

        assert success is False
        assert "Expected value different from 200" in error

    def test_compare_values_contains_success(self):
        """Test CONTAINS operator success."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(
            AssertionOperator.CONTAINS, "success message", "success"
        )

        assert success is True
        assert error == ""

    def test_compare_values_contains_failure(self):
        """Test CONTAINS operator failure."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(
            AssertionOperator.CONTAINS, "error message", "success"
        )

        assert success is False
        assert "Expected to find 'success' in response" in error

    def test_compare_values_less_than_success(self):
        """Test LESS_THAN operator success."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.LESS_THAN, 150, 200)

        assert success is True
        assert error == ""

    def test_compare_values_less_than_failure(self):
        """Test LESS_THAN operator failure."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.LESS_THAN, 250, 200)

        assert success is False
        assert "250 is not less than 200" in error

    def test_compare_values_more_than_success(self):
        """Test MORE_THAN operator success."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.MORE_THAN, 250, 200)

        assert success is True
        assert error == ""

    def test_compare_values_more_than_failure(self):
        """Test MORE_THAN operator failure."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(AssertionOperator.MORE_THAN, 150, 200)

        assert success is False
        assert "150 is not greater than 200" in error

    def test_compare_values_less_or_equals_success(self):
        """Test LESS_OR_EQUALS operator success."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(
            AssertionOperator.LESS_OR_EQUALS, 200, 200
        )

        assert success is True
        assert error == ""

    def test_compare_values_less_or_equals_failure(self):
        """Test LESS_OR_EQUALS operator failure."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(
            AssertionOperator.LESS_OR_EQUALS, 250, 200
        )

        assert success is False
        assert "250 is not less than or equal to 200" in error

    def test_compare_values_more_or_equals_success(self):
        """Test MORE_OR_EQUALS operator success."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(
            AssertionOperator.MORE_OR_EQUALS, 200, 200
        )

        assert success is True
        assert error == ""

    def test_compare_values_more_or_equals_failure(self):
        """Test MORE_OR_EQUALS operator failure."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(
            AssertionOperator.MORE_OR_EQUALS, 150, 200
        )

        assert success is False
        assert "150 is not greater than or equal to 200" in error

    def test_compare_values_unsupported_operator(self):
        """Test unsupported operator."""
        pinger = HttpPinger()

        success, error = pinger._compare_values("invalid_operator", 200, 200)

        assert success is False
        assert "Unsupported operator: invalid_operator" in error

    def test_compare_values_type_error(self):
        """Test type conversion error."""
        pinger = HttpPinger()

        success, error = pinger._compare_values(
            AssertionOperator.LESS_THAN, "not_a_number", 200
        )

        assert success is False
        assert "Failed to compare" in error

    def test_evaluate_assertion_success(self):
        """Test successful assertion evaluation."""
        pinger = HttpPinger()
        response = Mock()
        response.status_code = 200

        assertion = {
            "source": AssertionSource.STATUS_CODE,
            "operator": AssertionOperator.EQUALS,
            "target": 200,
            "property": None,
        }

        success, error = pinger._evaluate_assertion(assertion, response, 150)

        assert success is True
        assert error == ""

    def test_evaluate_assertion_missing_source(self):
        """Test assertion with missing source field."""
        pinger = HttpPinger()
        response = Mock()

        assertion = {
            "operator": AssertionOperator.EQUALS,
            "target": 200,
            "property": None,
        }

        success, error = pinger._evaluate_assertion(assertion, response, 150)

        assert success is False
        assert "missing required 'source' or 'operator'" in error

    def test_evaluate_assertion_missing_operator(self):
        """Test assertion with missing operator field."""
        pinger = HttpPinger()
        response = Mock()

        assertion = {
            "source": AssertionSource.STATUS_CODE,
            "target": 200,
            "property": None,
        }

        success, error = pinger._evaluate_assertion(assertion, response, 150)

        assert success is False
        assert "missing required 'source' or 'operator'" in error

    def test_evaluate_assertion_extract_failure(self):
        """Test assertion when value extraction fails."""
        pinger = HttpPinger()
        response = Mock()

        assertion = {
            "source": "invalid_source",
            "operator": AssertionOperator.EQUALS,
            "target": 200,
            "property": None,
        }

        success, error = pinger._evaluate_assertion(assertion, response, 150)

        assert success is False
        assert "Failed to extract invalid_source from response" in error

    def test_evaluate_assertion_comparison_failure(self):
        """Test assertion when comparison fails."""
        pinger = HttpPinger()
        response = Mock()
        response.status_code = 404

        assertion = {
            "source": AssertionSource.STATUS_CODE,
            "operator": AssertionOperator.EQUALS,
            "target": 200,
            "property": None,
        }

        success, error = pinger._evaluate_assertion(assertion, response, 150)

        assert success is False
        assert "Expected 200, got 404" in error


class TestHttpPingerExecute:
    """Test suite for HttpPinger.execute method."""

    @pytest.mark.asyncio
    async def test_execute_success_all_assertions_pass(self):
        """Test successful execution with all assertions passing."""
        pinger = HttpPinger(timeout_seconds=5)

        # Mock the httpx client and response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "ok"}'

        # Mock the httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                return_value=mock_response
            )

            assertions = [
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.EQUALS,
                    "target": 200,
                    "property": None,
                }
            ]

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={"User-Agent": "test"},
                body=None,
                assertions=assertions,
            )

            assert result.is_up is True
            assert result.status_code == 200
            assert result.response_time_ms is not None
            assert result.response_time_ms >= 0
            assert result.error_type is None

    @pytest.mark.asyncio
    async def test_execute_assertion_failure(self):
        """Test execution with assertion failure."""
        pinger = HttpPinger(timeout_seconds=5)

        mock_response = Mock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                return_value=mock_response
            )

            assertions = [
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.EQUALS,
                    "target": 200,
                    "property": None,
                }
            ]

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={},
                body=None,
                assertions=assertions,
            )

            assert result.is_up is False
            assert result.status_code == 404
            assert result.error_type == "assertion_failed"
            assert "Expected 200, got 404" in result.error_details["message"]

    @pytest.mark.asyncio
    async def test_execute_with_json_body(self):
        """Test execution with JSON body."""
        pinger = HttpPinger()

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_request = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.request = mock_request

            body = {"key": "value"}
            _ = await pinger.execute(
                url="https://example.com",
                method="POST",
                headers={},
                body=body,
                assertions=[],
            )

            # Verify that json parameter was used
            call_args = mock_request.call_args
            assert "json" in call_args.kwargs
            assert call_args.kwargs["json"] == body

    @pytest.mark.asyncio
    async def test_execute_with_string_body(self):
        """Test execution with string body."""
        pinger = HttpPinger()

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_request = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.request = mock_request

            body = "plain text body"
            _ = await pinger.execute(
                url="https://example.com",
                method="POST",
                headers={},
                body=body,
                assertions=[],
            )

            # Verify that content parameter was used
            call_args = mock_request.call_args
            assert "content" in call_args.kwargs
            assert call_args.kwargs["content"] == body

    @pytest.mark.asyncio
    async def test_execute_timeout_exception(self):
        """Test execution with timeout exception."""
        pinger = HttpPinger(timeout_seconds=1)

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={},
                body=None,
                assertions=[],
            )

            assert result.is_up is False
            assert result.error_type == "timeout"
            assert result.error_details["phase"] == "request"
            assert result.error_details["limit_ms"] == 1000
            assert "Request timed out" in result.error_details["message"]

    @pytest.mark.asyncio
    async def test_execute_connect_error(self):
        """Test execution with connection error."""
        pinger = HttpPinger()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={},
                body=None,
                assertions=[],
            )

            assert result.is_up is False
            assert result.error_type == "connection_refused"
            assert (
                "Connection refused or DNS resolution failed"
                in result.error_details["message"]
            )
            assert "Connection refused" in result.error_details["details"]

    @pytest.mark.asyncio
    async def test_execute_http_status_error(self):
        """Test execution with HTTP status error."""
        pinger = HttpPinger()

        # Create a mock response for the HTTPStatusError
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason_phrase = "Internal Server Error"

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Server error", request=Mock(), response=mock_response
                )
            )

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={},
                body=None,
                assertions=[],
            )

            assert result.is_up is False
            assert result.error_type == "http_error"
            assert result.status_code == 500
            assert result.error_details["status_code"] == 500
            assert result.error_details["reason"] == "Internal Server Error"

    @pytest.mark.asyncio
    async def test_execute_unknown_exception(self):
        """Test execution with unknown exception."""
        pinger = HttpPinger()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                side_effect=ValueError("Unexpected error")
            )

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={},
                body=None,
                assertions=[],
            )

            assert result.is_up is False
            assert result.error_type == "unknown_error"
            assert result.error_details["exception_type"] == "ValueError"
            assert "Unexpected error" in result.error_details["message"]

    @pytest.mark.asyncio
    async def test_execute_multiple_assertions_first_fails(self):
        """Test execution with multiple assertions where first fails."""
        pinger = HttpPinger()

        mock_response = Mock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                return_value=mock_response
            )

            assertions = [
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.EQUALS,
                    "target": 200,
                    "property": None,
                },
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.LESS_THAN,
                    "target": 500,
                    "property": None,
                },
            ]

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={},
                body=None,
                assertions=assertions,
            )

            assert result.is_up is False
            assert result.error_type == "assertion_failed"
            # Should fail on first assertion, not evaluate the second one
            assert result.error_details["failed_assertion"] == assertions[0]

    @pytest.mark.asyncio
    async def test_execute_complex_header_assertion(self):
        """Test execution with header assertion."""
        pinger = HttpPinger()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                return_value=mock_response
            )

            assertions = [
                {
                    "source": AssertionSource.HEADER,
                    "operator": AssertionOperator.CONTAINS,
                    "target": "json",
                    "property": "Content-Type",
                }
            ]

            result = await pinger.execute(
                url="https://example.com",
                method="GET",
                headers={},
                body=None,
                assertions=assertions,
            )

            assert result.is_up is True
            assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_execute_request_parameters(self):
        """Test that execute passes correct parameters to httpx."""
        pinger = HttpPinger(timeout_seconds=30)

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_request = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.request = mock_request

            await pinger.execute(
                url="https://api.example.com/test",
                method="PUT",
                headers={"Authorization": "Bearer token123"},
                body={"data": "test"},
                assertions=[],
            )

            # Verify request was called with correct parameters
            call_args = mock_request.call_args
            assert call_args.kwargs["method"] == "PUT"
            assert call_args.kwargs["url"] == "https://api.example.com/test"
            assert call_args.kwargs["headers"]["Authorization"] == "Bearer token123"
            assert call_args.kwargs["timeout"] == 30
            assert call_args.kwargs["follow_redirects"] is True
            assert call_args.kwargs["json"] == {"data": "test"}


class TestPingResult:
    """Test suite for PingResult model."""

    def test_ping_result_success(self):
        """Test creating a successful ping result."""
        result = PingResult(is_up=True, response_time_ms=150, status_code=200)

        assert result.is_up is True
        assert result.response_time_ms == 150
        assert result.status_code == 200
        assert result.error_type is None
        assert result.error_details == {}

    def test_ping_result_failure(self):
        """Test creating a failed ping result."""
        error_details = {
            "failed_assertion": {"source": "status_code"},
            "message": "Expected 200, got 404",
        }

        result = PingResult(
            is_up=False,
            response_time_ms=200,
            status_code=404,
            error_type="assertion_failed",
            error_details=error_details,
        )

        assert result.is_up is False
        assert result.response_time_ms == 200
        assert result.status_code == 404
        assert result.error_type == "assertion_failed"
        assert result.error_details == error_details

    def test_ping_result_defaults(self):
        """Test ping result with default values."""
        result = PingResult(is_up=False)

        assert result.is_up is False
        assert result.response_time_ms is None
        assert result.status_code is None
        assert result.error_type is None
        assert result.error_details == {}


@pytest.mark.skipif(
    os.getenv("RUN_LIVE") != "1",
    reason="Live tests disabled. Set RUN_LIVE=1 to execute httpbin integration tests.",
)
class TestHttpPingerLiveHttpbin:
    """Live integration tests for HttpPinger using httpbin.org."""

    @pytest.mark.asyncio
    async def test_live_status_code_equals_200(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/status/200",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.EQUALS,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_status_code_not_equals(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/status/404",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.NOT_EQUALS,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 404

    @pytest.mark.asyncio
    async def test_live_status_code_less_or_equals(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/status/200",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.LESS_OR_EQUALS,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_status_code_more_or_equals(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/status/200",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.MORE_OR_EQUALS,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_body_contains_json(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/json",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.BODY,
                    "operator": AssertionOperator.CONTAINS,
                    "target": "slideshow",
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_header_contains(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/response-headers?X-Test=sentinel-live",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.HEADER,
                    "operator": AssertionOperator.CONTAINS,
                    "target": "sentinel-live",
                    "property": "X-Test",
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_response_time_more_than(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/delay/1",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.RESPONSE_TIME,
                    "operator": AssertionOperator.MORE_THAN,
                    "target": 300,
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.response_time_ms is not None
        assert result.response_time_ms > 300

    @pytest.mark.asyncio
    async def test_live_response_time_less_than(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/delay/1",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.RESPONSE_TIME,
                    "operator": AssertionOperator.LESS_THAN,
                    "target": 6000,
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.response_time_ms is not None
        assert result.response_time_ms < 6000

    @pytest.mark.asyncio
    async def test_live_post_json_body(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/post",
            method="POST",
            headers={},
            body={"hello": "world"},
            assertions=[
                {
                    "source": AssertionSource.BODY,
                    "operator": AssertionOperator.CONTAINS,
                    "target": "hello",
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_post_string_body(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/post",
            method="POST",
            headers={"Content-Type": "text/plain"},
            body="plain text payload",
            assertions=[
                {
                    "source": AssertionSource.BODY,
                    "operator": AssertionOperator.CONTAINS,
                    "target": "plain text payload",
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_redirect_followed(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/redirect-to?url=/status/200",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.EQUALS,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_live_assertion_failure(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/status/404",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.STATUS_CODE,
                    "operator": AssertionOperator.EQUALS,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is False
        assert result.error_type == "assertion_failed"
        assert "Expected 200, got 404" in result.error_details["message"]

    @pytest.mark.asyncio
    async def test_live_invalid_source_assertion(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/status/200",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": "invalid_source",
                    "operator": AssertionOperator.EQUALS,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is False
        assert result.error_type == "assertion_failed"
        assert (
            "Failed to extract invalid_source from response"
            in result.error_details["message"]
        )

    @pytest.mark.asyncio
    async def test_live_missing_operator_assertion(self):
        pinger = HttpPinger(timeout_seconds=10)

        result = await pinger.execute(
            url="https://httpbin.org/status/200",
            method="GET",
            headers={},
            body=None,
            assertions=[
                {
                    "source": AssertionSource.STATUS_CODE,
                    "target": 200,
                    "property": None,
                }
            ],
        )

        assert result.is_up is False
        assert result.error_type == "assertion_failed"
        assert (
            "missing required 'source' or 'operator'" in result.error_details["message"]
        )

    @pytest.mark.asyncio
    async def test_live_timeout(self):
        pinger = HttpPinger(timeout_seconds=1)

        result = await pinger.execute(
            url="https://httpbin.org/delay/3",
            method="GET",
            headers={},
            body=None,
            assertions=[],
        )

        assert result.is_up is False
        assert result.error_type == "timeout"
