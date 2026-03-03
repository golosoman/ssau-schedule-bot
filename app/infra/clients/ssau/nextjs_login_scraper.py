import html
import json
import re
from collections import Counter
from urllib.parse import quote


class NextJsLoginScraper:
    DEFAULT_LOGIN_PAGE_PATH = "/api/account/logout"
    DEFAULT_FORM_STATE_KEY = "$K1"
    _LOGIN_CHUNK_RE = re.compile(
        r'src="(/_next/static/chunks/app/account/login/page-[^"]+\.js)"',
    )
    _LOGIN_CHUNK_FALLBACK_RE = re.compile(
        r'(/_next/static/chunks/app/account/login/page-[^"\'\\]+\.js)',
    )
    _ACTION_HASH_RE = re.compile(r"\b[a-f0-9]{40}\b")
    _ACTION_ENTRY_RE = re.compile(
        r"__next_internal_action_entry_do_not_use__\s*=\s*{([^}]+)}",
        re.S,
    )
    _ACTION_ENTRY_ID_RE = re.compile(r"['\"]([a-f0-9]{40})['\"]\s*:")
    _ACTION_ID_ASSIGN_RE = re.compile(r"\$\$ACTION_\d+\.\$\$id\s*=\s*['\"]([a-f0-9]{40})['\"]")
    _ACTION_ID_PROP_RE = re.compile(r"\$\$id\s*[:=]\s*['\"]([a-f0-9]{40})['\"]")
    _ACTION_HTML_ATTR_RE = re.compile(
        r'\b(?:data-)?next-action=["\']([a-f0-9]{40})["\']',
        re.I,
    )
    _ACTION_HTML_DATA_RE = re.compile(
        r'\bdata-action=["\']([a-f0-9]{40})["\']',
        re.I,
    )
    _ACTION_HTML_JSON_RE = re.compile(r'"actionId"\s*:\s*"([a-f0-9]{40})"')
    _NEXT_F_PUSH_RE = re.compile(
        r'self\.__next_f\.push\(\[\d+,\s*("(?:\\.|[^"\\])*")\s*\]\)',
        re.S,
    )
    _FORM_STATE_KEY_RE = re.compile(r"\$K\d+")
    _INPUT_TAG_RE = re.compile(r"<input[^>]*>", re.I)
    _INPUT_NAME_RE = re.compile(r'\bname=["\']([^"\']+)["\']', re.I)
    _INPUT_VALUE_RE = re.compile(r'\bvalue=(?:"([^"]*)"|\'([^\']*)\')', re.I)
    _TEXTAREA_RE = re.compile(
        r'<textarea[^>]*\bname=["\']([^"\']+)["\'][^>]*>(.*?)</textarea>',
        re.I | re.S,
    )

    @classmethod
    def extract_router_state(cls, html: str, route_path: str | None = None) -> str:
        tree = cls._extract_tree_from_text(html)
        if tree is None:
            raise RuntimeError("initialTree not found in login HTML")

        normalized = cls._normalize_router_state(tree, route_path)
        return quote(
            json.dumps(normalized, separators=(",", ":"), ensure_ascii=False),
            safe="",
        )

    @classmethod
    def extract_login_chunk_url(cls, html: str) -> str:
        match = cls._LOGIN_CHUNK_RE.search(html)
        if not match:
            match = cls._LOGIN_CHUNK_FALLBACK_RE.search(html)
        if not match:
            raise RuntimeError("login chunk URL not found in login HTML")
        return match.group(1)

    @classmethod
    def extract_next_action(cls, js: str) -> str:
        entry_ids = cls._extract_action_entry_ids(js)
        if len(entry_ids) == 1:
            return entry_ids[0]

        assign_ids = cls._ACTION_ID_ASSIGN_RE.findall(js)
        if len(assign_ids) == 1:
            return assign_ids[0]

        prop_ids = cls._ACTION_ID_PROP_RE.findall(js)
        if len(prop_ids) == 1:
            return prop_ids[0]

        if entry_ids:
            for pool in (assign_ids, prop_ids):
                intersection = set(entry_ids) & set(pool)
                if len(intersection) == 1:
                    return intersection.pop()

        hashes = cls._ACTION_HASH_RE.findall(js)
        if not hashes:
            raise RuntimeError("server action hash not found in login chunk")
        return Counter(hashes).most_common(1)[0][0]

    @classmethod
    def extract_next_action_from_html(cls, html_text: str) -> str | None:
        for pattern in (
            cls._ACTION_HTML_ATTR_RE,
            cls._ACTION_HTML_DATA_RE,
            cls._ACTION_HTML_JSON_RE,
        ):
            matches = pattern.findall(html_text)
            if len(matches) == 1:
                return matches[0]

        hashes = cls._ACTION_HASH_RE.findall(html_text)
        if len(hashes) == 1:
            return hashes[0]
        return None

    @classmethod
    def extract_page_path(cls, html_text: str) -> str | None:
        tree = cls._extract_tree_from_text(html_text)
        path = cls._get_page_path(tree) if tree else None
        if path and path.startswith("/"):
            return path
        for text in cls._iter_search_texts(html_text):
            if not isinstance(text, str):
                continue
            if cls.DEFAULT_LOGIN_PAGE_PATH in text:
                return cls.DEFAULT_LOGIN_PAGE_PATH
        return None

    @classmethod
    def extract_form_state(cls, html_text: str) -> str | None:
        value = cls.extract_form_value(html_text, "0")
        if value is not None:
            return value
        key = cls._extract_form_state_key(html_text)
        if key is None:
            key = cls.DEFAULT_FORM_STATE_KEY
        return json.dumps(
            [{"error": "", "fieldErrors": {}}, key],
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @classmethod
    def extract_form_value(cls, html_text: str, field_name: str) -> str | None:
        for tag in cls._INPUT_TAG_RE.findall(html_text):
            name_match = cls._INPUT_NAME_RE.search(tag)
            if not name_match or name_match.group(1) != field_name:
                continue
            value_match = cls._INPUT_VALUE_RE.search(tag)
            if not value_match:
                return ""
            raw_value = value_match.group(1) or value_match.group(2) or ""
            return html.unescape(raw_value)
        for name, value in cls._TEXTAREA_RE.findall(html_text):
            if name == field_name:
                return html.unescape(value).strip()
        return None

    @classmethod
    def _iter_search_texts(cls, html_text: str):
        yield html_text
        yield html.unescape(html_text)
        for raw in cls._NEXT_F_PUSH_RE.findall(html_text):
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            yield payload
            if isinstance(payload, str) and "\\\"" in payload:
                try:
                    yield bytes(payload, "utf-8").decode("unicode_escape")
                except UnicodeDecodeError:
                    continue

    @classmethod
    def _extract_form_state_key(cls, html_text: str) -> str | None:
        for text in cls._iter_search_texts(html_text):
            match = cls._FORM_STATE_KEY_RE.search(text)
            if match:
                return match.group(0)
        return None

    @classmethod
    def _extract_action_entry_ids(cls, js: str) -> list[str]:
        match = cls._ACTION_ENTRY_RE.search(js)
        if not match:
            return []
        return cls._ACTION_ENTRY_ID_RE.findall(match.group(1))

    @classmethod
    def _extract_tree_from_text(cls, text: str) -> list | None:
        trees: list[list] = []
        for candidate in cls._iter_search_texts(text):
            if not isinstance(candidate, str):
                continue
            trees.extend(cls._extract_all_trees(candidate))
        return cls._select_tree(trees)

    @classmethod
    def _extract_all_trees(cls, text: str) -> list[list]:
        trees: list[list] = []
        for match in re.finditer(r'"initialTree"\s*:', text):
            array_text = cls._extract_json_array(text, match.end())
            if not array_text:
                continue
            try:
                trees.append(json.loads(array_text))
            except json.JSONDecodeError:
                continue
        return trees

    @classmethod
    def _extract_json_array(cls, text: str, start_idx: int) -> str | None:
        idx = start_idx
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text) or text[idx] != "[":
            return None
        depth = 0
        in_string = False
        escape = False
        for pos in range(idx, len(text)):
            ch = text[pos]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return text[idx : pos + 1]
        return None

    @classmethod
    def _normalize_router_state(cls, tree: list, route_path: str | None) -> list:
        cleaned = cls._replace_undefined(tree)
        cls._ensure_layout_flags(cleaned)
        if route_path:
            cls._ensure_page_segment(cleaned, route_path, replace_invalid=True)
        return cleaned

    @classmethod
    def _replace_undefined(cls, value):
        if value == "$undefined":
            return None
        if isinstance(value, list):
            return [cls._replace_undefined(item) for item in value]
        if isinstance(value, dict):
            return {key: cls._replace_undefined(item) for key, item in value.items()}
        return value

    @classmethod
    def _ensure_page_segment(
        cls,
        node: list,
        route_path: str,
        *,
        replace_invalid: bool = False,
    ) -> None:
        if not isinstance(node, list) or len(node) < 2:
            return

        segment = node[0]
        if segment == "__PAGE__":
            if replace_invalid and len(node) >= 3:
                if not isinstance(node[2], str) or not node[2].startswith("/"):
                    node[2] = route_path
            if len(node) == 2:
                node.append(route_path)
            if len(node) == 3:
                node.append("refresh")
            return

        routes = node[1]
        if isinstance(routes, dict):
            for child in routes.values():
                if isinstance(child, list):
                    cls._ensure_page_segment(
                        child,
                        route_path,
                        replace_invalid=replace_invalid,
                    )

    @classmethod
    def _ensure_layout_flags(cls, node: list) -> None:
        if not isinstance(node, list) or len(node) < 2:
            return

        segment = node[0]
        routes = node[1]
        if segment != "__PAGE__" and isinstance(routes, dict):
            children = routes.get("children")
            if len(node) == 2 and isinstance(children, list) and children:
                if children[0] != "__PAGE__":
                    node.extend([None, None, True])
            for child in routes.values():
                if isinstance(child, list):
                    cls._ensure_layout_flags(child)

    @classmethod
    def _select_tree(cls, trees: list[list]) -> list | None:
        if not trees:
            return None
        for tree in trees:
            if cls._get_page_path(tree) == cls.DEFAULT_LOGIN_PAGE_PATH:
                return tree
        for tree in trees:
            path = cls._get_page_path(tree)
            if path and path.startswith("/"):
                return tree
        return trees[0]

    @classmethod
    def _get_page_path(cls, node: list) -> str | None:
        if not isinstance(node, list) or len(node) < 2:
            return None
        segment = node[0]
        if segment == "__PAGE__":
            if len(node) >= 3 and isinstance(node[2], str):
                return node[2]
            return None
        routes = node[1]
        if isinstance(routes, dict):
            for child in routes.values():
                if isinstance(child, list):
                    path = cls._get_page_path(child)
                    if path:
                        return path
        return None
