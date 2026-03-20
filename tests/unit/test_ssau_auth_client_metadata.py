import json
from typing import Any, cast
from urllib.parse import unquote

import pytest

from app.infra.clients.ssau.auth_client import AuthClient
from app.infra.clients.ssau.nextjs_login_scraper import NextJsLoginScraper

ACTION_ID = "60e1b506aa72f3dc090b62cc3f8ab44ef5c5569bc5"


def _build_new_login_html(action_id: str = ACTION_ID) -> str:
    flight_root = {
        "P": None,
        "c": ["", "account", "login"],
        "f": [
            [
                [
                    "",
                    {
                        "children": [
                            "account",
                            {
                                "children": [
                                    "login",
                                    {
                                        "children": ["__PAGE__", {}],
                                    },
                                ],
                            },
                        ],
                    },
                    "$undefined",
                    "$undefined",
                    16,
                ],
                {},
                None,
                False,
                None,
            ]
        ],
    }
    flight_payload = "0:" + json.dumps(
        flight_root,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    action_payload = json.dumps(
        {"id": action_id, "bound": "$@1"},
        separators=(",", ":"),
        ensure_ascii=False,
    )
    escaped_action_payload = action_payload.replace('"', "&quot;")

    return (
        '<form method="POST" enctype="multipart/form-data">'
        f'<input type="hidden" name="$ACTION_1:0" value="{escaped_action_payload}"/>'
        '<input type="hidden" name="$ACTION_1:1" '
        'value="[{&quot;error&quot;:&quot;&quot;,&quot;fieldErrors&quot;:{}}]"/>'
        '<input type="hidden" name="$ACTION_KEY" value="k123"/>'
        '<input type="hidden" name="returnUrl" value=""/>'
        "</form>"
        f"<script>self.__next_f.push([1,{json.dumps(flight_payload)}])</script>"
    )


def _extract_page_node(tree: list) -> list:
    account_node = tree[1]["children"][1]
    login_node = account_node["children"][1]
    return login_node["children"]


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}")


class _FakeClient:
    def __init__(self, html: str) -> None:
        self._html = html
        self.calls: list[str] = []

    async def get(self, path: str, *, headers: dict[str, str]) -> _FakeResponse:
        self.calls.append(path)
        if path == "/account/login":
            return _FakeResponse(self._html)
        raise AssertionError(f"unexpected GET path: {path}")


@pytest.mark.asyncio
async def test_fetch_login_metadata_uses_html_flight_without_chunk() -> None:
    fake_client = _FakeClient(_build_new_login_html())
    auth_client = AuthClient(
        client=cast(Any, fake_client),
        scraper=NextJsLoginScraper(),
    )

    router_state, next_action, form_state, return_url = await auth_client._fetch_login_metadata()
    decoded_state = json.loads(unquote(router_state))
    page_node = _extract_page_node(decoded_state)

    assert fake_client.calls == ["/account/login"]
    assert next_action == ACTION_ID
    assert form_state == '[{"error":"","fieldErrors":{}},"$K1"]'
    assert return_url == ""
    assert page_node[2] == "/account/login"
