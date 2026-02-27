import httpx


class HttpClientFactory:
    @staticmethod
    def create(
        base_url: str,
        login_path: str,
        *,
        timeout_seconds: float = 15.0,
    ) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=base_url,
            follow_redirects=True,
            timeout=httpx.Timeout(timeout_seconds),
            headers={
                "accept": "text/x-component",
                "origin": base_url,
                "referer": f"{base_url}{login_path}",
                "user-agent": "Mozilla/5.0",
            },
        )
