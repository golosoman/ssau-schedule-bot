import httpx

from app.app_layer.interfaces.http.ssau.auth.interface import ISsauAuthClient
from app.domain.entities.auth import AuthSession
from app.infra.clients.http.client import BaseHttpClient
from app.infra.clients.http.options import BaseHttpClientOption, WithMetrics, WithRetry
from app.infra.clients.ssau.auth.scraper import NextJsLoginScraper
from app.infra.clients.ssau.metrics import SsauHttpClientMetrics
from app.infra.clients.ssau.settings import SSAUClientSettings
from app.infra.observability.metrics.interface import IMetricsService
from app.infra.retry import RetryableError, RetryPolicy, retry_async
from app.logging.config import get_logger

logger = get_logger(__name__)

LOGIN_PATH = "/account/login"


def ssau_default_headers(base_url: str) -> dict[str, str]:
    """Shared SSAU request headers (Next.js server actions expect these)."""
    return {
        "accept": "text/x-component",
        "origin": base_url,
        "referer": f"{base_url}{LOGIN_PATH}",
        "user-agent": "Mozilla/5.0",
    }


class SsauAuthClient(BaseHttpClient, ISsauAuthClient):
    """Performs the SSAU Next.js login flow and returns the ``auth`` cookie.

    The login is a reverse-engineered server-action submission: it scrapes the
    login page (and, if needed, the page JS chunk) for the ``next-action`` id,
    router-state tree and form state, then POSTs the credentials.
    """

    _LOGIN_PATH = LOGIN_PATH
    _RETRY_STATUSES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        *,
        settings: SSAUClientSettings,
        retry_policy: RetryPolicy | None = None,
        scraper: NextJsLoginScraper | None = None,
        metrics_service: IMetricsService | None = None,
    ) -> None:
        options: list[BaseHttpClientOption] = []
        if metrics_service is not None:
            options.append(WithMetrics(SsauHttpClientMetrics(metrics_service)))
        if retry_policy is not None:
            options.append(WithRetry(retry_policy))
        super().__init__(
            "ssau-auth",
            settings.base_url,
            *options,
            timeout_seconds=settings.timeout_seconds,
            default_headers=ssau_default_headers(settings.base_url),
        )
        self._settings = settings
        self._scraper = scraper or NextJsLoginScraper()
        self._login_retry_policy = retry_policy

    async def login(self, login: str, password: str) -> AuthSession:
        try:
            return await self._login(login, password)
        finally:
            self.clear_cookies()

    async def _login(self, login: str, password: str) -> AuthSession:
        async def _operation() -> AuthSession:
            router_state, next_action, form_state, return_url = await self._fetch_login_metadata()
            if return_url is None:
                return_url = ""

            request = self.build_request(
                "POST",
                self._LOGIN_PATH,
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
            response = await self.send(request, stream=True, follow_redirects=False)
            auth_cookie: str | None = None
            try:
                if response.status_code in self._RETRY_STATUSES:
                    logger.warning(
                        "SSAU login retryable status: status=%s next_action=%s "
                        "router_state=%s return_url=%s form_state=%s",
                        response.status_code,
                        next_action,
                        router_state,
                        return_url,
                        form_state,
                    )
                    raise RetryableError(f"SSAU login retryable status: {response.status_code}")
                if response.is_error:
                    logger.error(
                        "SSAU login failed: status=%s next_action=%s "
                        "router_state=%s return_url=%s form_state=%s",
                        response.status_code,
                        next_action,
                        router_state,
                        return_url,
                        form_state,
                    )
                    response.raise_for_status()
                auth_cookie = response.cookies.get("auth")
            finally:
                await response.aclose()

            if auth_cookie is None and self._session is not None:
                auth_cookie = self._session.cookies.get("auth")

            if auth_cookie is None:
                raise RuntimeError("Login failed: auth cookie not set")

            logger.info("SSAU login succeeded.")
            return AuthSession(auth_cookie=auth_cookie)

        if self._login_retry_policy is None:
            return await _operation()

        def _on_retry(exc: Exception, delay: float, attempt: int) -> None:
            logger.warning("SSAU login retry %s in %.2fs (%s)", attempt, delay, exc)

        return await retry_async(
            _operation,
            policy=self._login_retry_policy,
            is_retryable=lambda exc: isinstance(exc, (httpx.RequestError, RetryableError)),
            on_retry=_on_retry,
        )

    async def _fetch_login_metadata(self) -> tuple[str, str, str | None, str | None]:
        response = await self.get(
            self._LOGIN_PATH,
            headers={"accept": "text/html"},
        )
        response.raise_for_status()

        html = response.text
        form_state = self._scraper.extract_form_state(html)
        form_state_source = "html"
        return_url = self._scraper.extract_form_value(html, "1_returnUrl")
        return_url_field = "1_returnUrl"
        if return_url is None:
            return_url = self._scraper.extract_form_value(html, "returnUrl")
            return_url_field = "returnUrl" if return_url is not None else "missing"
        page_path = self._scraper.extract_page_path(html)
        page_path_source = "html"
        next_action = self._scraper.extract_next_action_from_html(html)
        next_action_source = "html"

        need_js = (
            next_action is None
            or form_state is None
            or page_path is None
            or not page_path.startswith("/")
        )
        js_text: str | None = None
        if need_js:
            try:
                chunk_url = self._scraper.extract_login_chunk_url(html)
            except RuntimeError:
                logger.warning(
                    "SSAU login metadata: login chunk URL unavailable "
                    "(next_action=%s page_path=%s form_state=%s).",
                    next_action is not None,
                    page_path,
                    form_state is not None,
                )
            else:
                js_response = await self.get(
                    chunk_url,
                    headers={"accept": "*/*"},
                )
                js_response.raise_for_status()
                js_text = js_response.text
                logger.info("SSAU login metadata: loaded login chunk %s", chunk_url)

        if next_action is None and js_text is not None:
            next_action = self._scraper.extract_next_action(js_text)
            next_action_source = "js_chunk"
        if form_state is None and js_text is not None:
            form_state = self._scraper.extract_form_state(js_text)
            form_state_source = "js_chunk"
        if (page_path is None or not page_path.startswith("/")) and js_text is not None:
            page_path = self._scraper.extract_page_path(js_text)
            if page_path is not None and page_path.startswith("/"):
                page_path_source = "js_chunk"

        if next_action is None:
            raise RuntimeError("next-action not found in login HTML/JS")

        page_path = page_path or self._scraper.DEFAULT_LOGIN_PAGE_PATH
        if page_path_source == "html" and page_path == self._scraper.DEFAULT_LOGIN_PAGE_PATH:
            page_path_source = "default"
        if not page_path.startswith("/"):
            page_path = self._LOGIN_PATH
            page_path_source = "login_path_fallback"

        router_state_source = "html_or_flight"
        try:
            router_state = self._scraper.extract_router_state(
                html,
                route_path=page_path,
            )
        except RuntimeError:
            if js_text is None:
                raise
            router_state = self._scraper.extract_router_state(
                js_text,
                route_path=page_path,
            )
            router_state_source = "js_chunk"

        logger.info(
            "SSAU login metadata resolved: next_action_source=%s page_path_source=%s "
            "router_state_source=%s form_state_source=%s return_url_field=%s",
            next_action_source,
            page_path_source,
            router_state_source,
            form_state_source,
            return_url_field,
        )
        return router_state, next_action, form_state, return_url
