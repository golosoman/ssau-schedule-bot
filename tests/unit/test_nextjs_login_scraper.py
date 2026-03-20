import json
from urllib.parse import unquote

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
        '<input type="hidden" name="$ACTION_REF_1"/>'
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


def test_extract_next_action_from_hidden_input_supports_new_length() -> None:
    html = _build_new_login_html()
    assert NextJsLoginScraper.extract_next_action_from_html(html) == ACTION_ID


def test_extract_page_path_from_flight_payload() -> None:
    html = _build_new_login_html()
    assert NextJsLoginScraper.extract_page_path(html) == "/account/login"


def test_extract_router_state_from_flight_tree_without_initial_tree() -> None:
    html = _build_new_login_html()
    encoded_state = NextJsLoginScraper.extract_router_state(
        html,
        route_path="/account/login",
    )
    decoded_state = json.loads(unquote(encoded_state))
    page_node = _extract_page_node(decoded_state)

    assert page_node[0] == "__PAGE__"
    assert page_node[2] == "/account/login"
    assert page_node[3] == "refresh"


def test_legacy_initial_tree_path_still_supported() -> None:
    legacy_tree = [
        "",
        {
            "children": [
                "account",
                {
                    "children": [
                        "login",
                        {
                            "children": [
                                "__PAGE__",
                                {},
                                "/api/account/logout",
                                "refresh",
                            ],
                        },
                    ],
                },
                None,
                None,
                True,
            ],
        },
        None,
        None,
        True,
    ]
    html = (
        "<script>"
        + json.dumps({"initialTree": legacy_tree}, separators=(",", ":"), ensure_ascii=False)
        + "</script>"
    )

    path = NextJsLoginScraper.extract_page_path(html)
    encoded_state = NextJsLoginScraper.extract_router_state(
        html,
        route_path="/api/account/logout",
    )
    decoded_state = json.loads(unquote(encoded_state))
    page_node = _extract_page_node(decoded_state)

    assert path == "/api/account/logout"
    assert page_node[2] == "/api/account/logout"
