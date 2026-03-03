import logging

import httpx

from app.app_layer.interfaces.http.ssau.interface import AuthRepository
from app.domain.entities.auth import AuthSession
from app.infra.clients.ssau.nextjs_login_scraper import (
    NextJsLoginScraper,
)
from app.infra.retry import RetryPolicy, RetryableError, retry_async

logger = logging.getLogger(__name__)


class AuthClient(AuthRepository):
    _LOGIN_PATH = "/account/login"
    _RETRY_STATUSES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        client: httpx.AsyncClient,
        scraper: NextJsLoginScraper | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._client = client
        self._login_path = self._LOGIN_PATH
        self._scraper = scraper or NextJsLoginScraper()
        self._retry_policy = retry_policy

    async def login(self, login: str, password: str) -> AuthSession:
        async def _operation() -> AuthSession:
            router_state, next_action, form_state, return_url = await self._fetch_login_metadata()
            if return_url is None:
                return_url = ""

            request = self._client.build_request(
                "POST",
                self._login_path,
                headers={
                    "next-action": next_action,
                    "next-router-state-tree": router_state,
                },
                files={
                    "1_returnUrl": (None, return_url),
                    "1_login": (None, login),
                    "1_password": (None, password),
                    "0": (None, form_state or ""),
                },
            )
            try:
                response = await self._client.send(
                    request,
                    stream=True,
                    follow_redirects=False,
                )
            except TypeError:
                response = await self._client.send(request, stream=True)
            try:
                if response.status_code in self._RETRY_STATUSES:
                    logger.warning(
                        "SSAU login retryable status: status=%s next_action=%s router_state=%s return_url=%s form_state=%s",
                        response.status_code,
                        next_action,
                        router_state,
                        return_url,
                        form_state,
                    )
                    raise RetryableError(f"SSAU login retryable status: {response.status_code}")
                if response.is_error:
                    logger.error(
                        "SSAU login failed: status=%s next_action=%s router_state=%s return_url=%s form_state=%s",
                        response.status_code,
                        next_action,
                        router_state,
                        return_url,
                        form_state,
                    )
                    response.raise_for_status()
            finally:
                await response.aclose()

            if "auth" not in self._client.cookies:
                raise RuntimeError("Login failed: auth cookie not set")

            logger.info("SSAU login succeeded.")
            return AuthSession(auth_cookie=self._client.cookies["auth"])

        if self._retry_policy is None:
            return await _operation()

        def _on_retry(exc: Exception, delay: float, attempt: int) -> None:
            logger.warning("SSAU login retry %s in %.2fs (%s)", attempt, delay, exc)

        return await retry_async(
            _operation,
            policy=self._retry_policy,
            is_retryable=lambda exc: isinstance(exc, (httpx.RequestError, RetryableError)),
            on_retry=_on_retry,
        )

    async def _fetch_login_metadata(self) -> tuple[str, str, str | None, str | None]:
        response = await self._client.get(
            self._login_path,
            headers={"accept": "text/html"},
        )
        response.raise_for_status()

        html = response.text
        form_state = self._scraper.extract_form_state(html)
        return_url = self._scraper.extract_form_value(html, "1_returnUrl")
        page_path = self._scraper.extract_page_path(html)
        next_action = self._scraper.extract_next_action_from_html(html)

        need_js = (
            next_action is None
            or form_state is None
            or page_path is None
            or not page_path.startswith("/")
        )
        js_text = None
        if need_js:
            chunk_url = self._scraper.extract_login_chunk_url(html)
            js_response = await self._client.get(
                chunk_url,
                headers={"accept": "*/*"},
            )
            js_response.raise_for_status()
            js_text = js_response.text

        if next_action is None and js_text is not None:
            next_action = self._scraper.extract_next_action(js_text)
        if form_state is None and js_text is not None:
            form_state = self._scraper.extract_form_state(js_text)
        if (page_path is None or not page_path.startswith("/")) and js_text is not None:
            page_path = self._scraper.extract_page_path(js_text)

        page_path = page_path or self._scraper.DEFAULT_LOGIN_PAGE_PATH
        if not page_path.startswith("/"):
            page_path = self._login_path

        router_state = self._scraper.extract_router_state(
            html,
            route_path=page_path,
        )
        return router_state, next_action, form_state, return_url
