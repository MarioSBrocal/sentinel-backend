import time
from typing import Any

import httpx
from pydantic import BaseModel

from app.schemas.monitor import AssertionOperator, AssertionSource


class PingResult(BaseModel):
    """Result of an HTTP ping operation containing status and performance metrics."""

    is_up: bool
    response_time_ms: int | None = None
    status_code: int | None = None
    error_type: str | None = None
    error_details: dict[str, Any] = {}


class HttpPinger:
    """
    Executes HTTP requests to monitored endpoints and evaluates their health based on custom assertion rules."""

    def __init__(self, timeout_seconds: int = 10):
        """
        Initialize the HTTP pinger.

        Arguments
        ---------
            timeout_seconds: Maximum time to wait for a response before timing out.
        """
        self.timeout = timeout_seconds

    def _extract_actual_value(
        self,
        source: str,
        response: httpx.Response,
        elapsed_ms: int,
        property_name: str | None,
    ) -> Any:
        """
        Extract the actual value from the HTTP response based on the assertion source.

        Parameters
        ----------
            source: What to extract (status_code, response_time, header, body).
            response: The HTTP response object.
            elapsed_ms: Response time in milliseconds.
            property_name: For headers, the name of the header to extract.

        Returns
        -------
            The extracted value from the response.

        Raises:
            ValueError: If the source cannot be extracted from the response.
        """
        if source == AssertionSource.STATUS_CODE:
            return response.status_code

        if source == AssertionSource.RESPONSE_TIME:
            return elapsed_ms

        if source == AssertionSource.HEADER:
            if not property_name:
                raise ValueError("Header assertions require a property name")
            return response.headers.get(property_name)

        if source == AssertionSource.BODY:
            return response.text

        raise ValueError(f"Unknown assertion source: {source}")

    def _compare_values(
        self, operator: str, actual_value: Any, target: Any
    ) -> tuple[bool, str]:
        """
        Compare actual and target values using the specified operator.

        Parameters
        ----------
            operator: `str` Comparison operator (equals, contains, less_than, etc.).
            actual_value: `Any` The actual value from the response.
            target: `Any` The expected target value.

        Returns
        -------
            A tuple of (success: bool, error_message: str).
            If success is True, error_message is empty.
        """
        try:
            if operator == AssertionOperator.EQUALS:
                if actual_value == target:
                    return True, ""
                return False, f"Expected {target}, got {actual_value}"

            if operator == AssertionOperator.NOT_EQUALS:
                if actual_value != target:
                    return True, ""
                return False, f"Expected value different from {target}, but got it"

            if operator == AssertionOperator.CONTAINS:
                if target in str(actual_value):
                    return True, ""
                return False, f"Expected to find '{target}' in response"

            if operator == AssertionOperator.LESS_THAN:
                if float(actual_value) < float(target):
                    return True, ""
                return False, f"{actual_value} is not less than {target}"

            if operator == AssertionOperator.MORE_THAN:
                if float(actual_value) > float(target):
                    return True, ""
                return False, f"{actual_value} is not greater than {target}"

            if operator == AssertionOperator.LESS_OR_EQUALS:
                if float(actual_value) <= float(target):
                    return True, ""
                return False, f"{actual_value} is not less than or equal to {target}"

            if operator == AssertionOperator.MORE_OR_EQUALS:
                if float(actual_value) >= float(target):
                    return True, ""
                return False, f"{actual_value} is not greater than or equal to {target}"

            return False, f"Unsupported operator: {operator}"

        except (TypeError, ValueError) as e:
            return (
                False,
                f"Failed to compare {actual_value} with {target} using {operator}: {e}",
            )

    def _evaluate_assertion(
        self, assertion: dict[str, Any], response: httpx.Response, elapsed_ms: int
    ) -> tuple[bool, str]:
        """
        Evaluate a single assertion rule against the HTTP response.

        Parameters
        ----------
            assertion: `dict[str, Any]` Dict containing source, operator, target, and optional property.
            response: `httpx.Response` The HTTP response object.
            elapsed_ms: `int` Response time in milliseconds.

        Returns
        -------
            A tuple of (success: bool, error_message: str).
            If success is True, error_message is empty.
        """
        source = assertion.get("source")
        operator = assertion.get("operator")
        target = assertion.get("target")
        property_name = assertion.get("property")

        # Validate required fields
        if not source or not operator:
            return False, "Assertion missing required 'source' or 'operator' field"

        # Extract the actual value from the response
        try:
            actual_value = self._extract_actual_value(
                source, response, elapsed_ms, property_name
            )
        except Exception as e:
            return False, f"Failed to extract {source} from response: {e}"

        # Compare using the specified operator
        return self._compare_values(operator, actual_value, target)

    async def execute(
        self,
        url: str,
        method: str,
        headers: dict[str, str],
        body: dict | str | None,
        assertions: list[dict[str, Any]],
    ) -> PingResult:
        """
        Execute an HTTP request and evaluate the response against assertion rules.

        Parameters
        ----------
            url: `str` The endpoint URL to ping.
            method: `str` HTTP method (GET, POST, PUT, etc.).
            headers: `dict[str, str]` HTTP headers to include in the request.
            body: `dict | str | None` Optional request body (dict for JSON, str for plain text).
            assertions: `list[dict[str, Any]]` List of validation rules to check.

        Returns
        -------
            `PingResult`: containing the status and performance metrics.
        """
        start_time = time.perf_counter()

        # Prepare request parameters
        request_kwargs: dict[str, Any] = {
            "method": method,
            "url": url,
            "headers": headers,
            "timeout": self.timeout,
            "follow_redirects": True,
        }

        # httpx uses 'json=' for dicts and 'content=' for strings/bytes
        if body:
            if isinstance(body, dict):
                request_kwargs["json"] = body
            else:
                request_kwargs["content"] = str(body)

        try:
            # Execute the HTTP request
            async with httpx.AsyncClient() as client:
                response = await client.request(**request_kwargs)

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # Evaluate all assertions
            for assertion in assertions:
                success, error_message = self._evaluate_assertion(
                    assertion, response, elapsed_ms
                )

                if not success:
                    return PingResult(
                        is_up=False,
                        response_time_ms=elapsed_ms,
                        status_code=response.status_code,
                        error_type="assertion_failed",
                        error_details={
                            "failed_assertion": assertion,
                            "message": error_message,
                        },
                    )

            # All assertions passed - monitor is UP
            return PingResult(
                is_up=True,
                response_time_ms=elapsed_ms,
                status_code=response.status_code,
            )

        except httpx.TimeoutException:
            return PingResult(
                is_up=False,
                error_type="timeout",
                error_details={
                    "phase": "request",
                    "elapsed_ms": int((time.perf_counter() - start_time) * 1000),
                    "limit_ms": self.timeout * 1000,
                    "message": "Request timed out",
                },
            )

        except httpx.ConnectError as e:
            return PingResult(
                is_up=False,
                error_type="connection_refused",
                error_details={
                    "message": "Connection refused or DNS resolution failed",
                    "details": str(e),
                },
            )

        except httpx.HTTPStatusError as e:
            return PingResult(
                is_up=False,
                response_time_ms=int((time.perf_counter() - start_time) * 1000),
                status_code=e.response.status_code,
                error_type="http_error",
                error_details={
                    "status_code": e.response.status_code,
                    "reason": e.response.reason_phrase,
                    "message": str(e),
                },
            )

        except Exception as e:
            return PingResult(
                is_up=False,
                error_type="unknown_error",
                error_details={
                    "exception_type": type(e).__name__,
                    "message": str(e),
                },
            )
