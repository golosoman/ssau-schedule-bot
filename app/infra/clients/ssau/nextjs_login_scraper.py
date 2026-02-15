import json
import re
from collections import Counter
from urllib.parse import quote


class NextJsLoginScraper:
    _INITIAL_TREE_RE = re.compile(
        r'"initialTree":(\[.*?\])\s*,\s*"initialSeedData"',
        re.S,
    )
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
    _ACTION_ID_ASSIGN_RE = re.compile(
        r"\$\$ACTION_\d+\.\$\$id\s*=\s*['\"]([a-f0-9]{40})['\"]"
    )
    _ACTION_ID_PROP_RE = re.compile(r"\$\$id\s*[:=]\s*['\"]([a-f0-9]{40})['\"]")
    _NEXT_F_PUSH_RE = re.compile(
        r'self\.__next_f\.push\(\[\d+,\s*("(?:\\.|[^"\\])*")\s*\]\)',
        re.S,
    )

    @classmethod
    def extract_router_state(cls, html: str, route_path: str | None = None) -> str:
        tree = cls._extract_tree_from_text(html)
        if tree is None:
            tree = cls._extract_tree_from_next_f_payload(html)
        if tree is None:
            raise RuntimeError("initialTree not found in login HTML")

        normalized = cls._normalize_router_state(tree, route_path)
        return quote(json.dumps(normalized, separators=(",", ":"), ensure_ascii=False))

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
    def _extract_action_entry_ids(cls, js: str) -> list[str]:
        match = cls._ACTION_ENTRY_RE.search(js)
        if not match:
            return []
        return cls._ACTION_ENTRY_ID_RE.findall(match.group(1))

    @classmethod
    def _extract_tree_from_text(cls, text: str) -> list | None:
        match = cls._INITIAL_TREE_RE.search(text)
        if not match:
            return None
        return json.loads(match.group(1))

    @classmethod
    def _extract_tree_from_next_f_payload(cls, html: str) -> list | None:
        payloads = []
        for raw in cls._NEXT_F_PUSH_RE.findall(html):
            try:
                payloads.append(json.loads(raw))
            except json.JSONDecodeError:
                continue

        if not payloads:
            return None

        combined = "".join(payloads)
        match = cls._INITIAL_TREE_RE.search(combined)
        if not match:
            return None
        return json.loads(match.group(1))

    @classmethod
    def _normalize_router_state(cls, tree: list, route_path: str | None) -> list:
        cleaned = cls._replace_undefined(tree)
        if route_path:
            cls._ensure_page_segment(cleaned, route_path)
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
    def _ensure_page_segment(cls, node: list, route_path: str) -> None:
        if not isinstance(node, list) or len(node) < 2:
            return

        segment = node[0]
        if segment == "__PAGE__":
            if len(node) == 2:
                node.append(route_path)
            if len(node) == 3:
                node.append("refresh")
            return

        routes = node[1]
        if isinstance(routes, dict):
            for child in routes.values():
                if isinstance(child, list):
                    cls._ensure_page_segment(child, route_path)
