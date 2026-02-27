import json
import logging

import httpx

from app.app_layer.interfaces.http.ssau.interface import AuthRepository
from app.domain.entities.auth import AuthSession
from app.infra.clients.ssau.nextjs_login_scraper import (
    NextJsLoginScraper,
)

logger = logging.getLogger(__name__)


class AuthClient(AuthRepository):
    _LOGIN_PATH = "/account/login"

    def __init__(
        self,
        client: httpx.AsyncClient,
        scraper: NextJsLoginScraper | None = None,
    ) -> None:
        self._client = client
        self._login_path = self._LOGIN_PATH
        self._scraper = scraper or NextJsLoginScraper()

    async def login(self, login: str, password: str) -> AuthSession:
        router_state, next_action = await self._fetch_login_metadata()

        response = await self._client.post(
            self._login_path,
            headers={
                "next-action": next_action,
                "next-router-state-tree": router_state,
            },
            files={
                "1_returnUrl": (None, "/"),
                "1_login": (None, login),
                "1_password": (None, password),
                "0": (None, ""),
            },
            follow_redirects=False,
        )
        if response.is_error:
            response.raise_for_status()

        if "auth" not in self._client.cookies:
            raise RuntimeError("Login failed: auth cookie not set")

        logger.info("SSAU login succeeded.")
        return AuthSession(auth_cookie=self._client.cookies["auth"])

    async def _fetch_login_metadata(self) -> tuple[str, str]:
        response = await self._client.get(
            self._login_path,
            headers={"accept": "text/html"},
        )
        response.raise_for_status()

        html = response.text
        router_state = self._scraper.extract_router_state(
            html,
            route_path=self._login_path,
        )
        chunk_url = self._scraper.extract_login_chunk_url(html)

        js_response = await self._client.get(
            chunk_url,
            headers={"accept": "*/*"},
        )
        js_response.raise_for_status()

        next_action = self._scraper.extract_next_action(js_response.text)
        return router_state, next_action
