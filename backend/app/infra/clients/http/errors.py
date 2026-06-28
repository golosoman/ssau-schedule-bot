from app.infra.retry import RetryableError


class RetryableHttpStatusError(RetryableError):
    def __init__(self, status_code: int, retry_after: float | None) -> None:
        super().__init__(
            f"Retryable HTTP status: {status_code}",
            retry_after=retry_after,
        )
        self.status_code = status_code
