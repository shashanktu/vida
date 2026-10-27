import json
import re
import xml.etree.ElementTree as _StdET
from typing import Any, Callable

import yaml  # pip install pyyaml

try:  # safer XML parsing if available: pip install defusedxml
    from defusedxml import ElementTree as ET
except ImportError:
    ET = _StdET

from vida.utils.logger import get_logger

logger = get_logger(__name__)

MAX_DEPTH = 8          # recursion guard
MIN_OUTLINE_SIGNALS = 2  # how many headers/bullets/"key: value" lines before text counts as structured


# --------------------------------------------------------------------------
# Kept for backward compatibility
# --------------------------------------------------------------------------
def clean_yaml_output(yaml_str):
    logger.info("[clean_yaml_output] Cleaning YAML output.")
    lines = [l for l in yaml_str.splitlines() if not l.strip().startswith("```")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Generic helpers
# --------------------------------------------------------------------------
def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    if hasattr(value, "__dict__"):
        return _to_jsonable(value.__dict__)
    return str(value)  # dates, enums, etc.


_FENCE = re.compile(r"^\s*```[\w+-]*[ \t]*\n(.*?)\n?```\s*$", re.DOTALL)


def _strip_fences(text: str) -> str:
    m = _FENCE.match(text)
    return (m.group(1) if m else text).strip("\n")


# --------------------------------------------------------------------------
# Parser 1: JSON (including double-encoded JSON)
# --------------------------------------------------------------------------
def _try_json(s: str):
    try:
        obj = json.loads(s)
    except ValueError:
        return s, False
    for _ in range(3):  # "\"{\\\"a\\\": 1}\"" -> '{"a": 1}' -> {"a": 1}
        if not isinstance(obj, str):
            break
        try:
            obj = json.loads(obj)
        except ValueError:
            break
    return (obj, True) if isinstance(obj, (dict, list)) else (s, False)


# --------------------------------------------------------------------------
# Parser 2: XML
# --------------------------------------------------------------------------
def _xml_to_obj(el) -> Any:
    obj: dict[str, Any] = {f"@{k}": v for k, v in el.attrib.items()}
    for child in el:
        val = _xml_to_obj(child)
        if child.tag in obj:
            if not isinstance(obj[child.tag], list):
                obj[child.tag] = [obj[child.tag]]
            obj[child.tag].append(val)
        else:
            obj[child.tag] = val
    text = (el.text or "").strip()
    if text:
        if not obj:
            return text
        obj["#text"] = text
    return obj or None


def _try_xml(s: str):
    t = s.strip()
    if not (t.startswith("<") and t.endswith(">")):
        return s, False
    root = ET.fromstring(t)  # raises on bad XML; caught by the caller
    return {root.tag: _xml_to_obj(root)}, True


# --------------------------------------------------------------------------
# Parser 3: YAML (strict; only mappings/sequences count)
# --------------------------------------------------------------------------
def _try_yaml(s: str):
    parsed = yaml.safe_load(s)
    return (parsed, True) if isinstance(parsed, (dict, list)) else (s, False)


# --------------------------------------------------------------------------
# Parser 4: tolerant outline parser (headers, bullets, numbered lists,
# "Key: value" lines, markdown headings). Handles LLM-style text that is
# almost-but-not-quite valid YAML (backticks, colons inside values, etc.)
# --------------------------------------------------------------------------
_BULLET = re.compile(r"^(?:[-*+]|\d+[.)])\s+(.*)$")
_MD_HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
_KV = re.compile(r"^([^:`]{1,60}?):\s+(\S.*)$")


def _tokenize(text: str):
    rows, level = [], 0  # row = (indent, kind, text, is_header)
    for raw in text.expandtabs(4).splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        s = raw.strip()

        h = _MD_HEAD.match(s)
        if h:
            level = len(h.group(1))
            rows.append(((level - 1) * 2, "head", h.group(2).strip().rstrip(":"), True))
            continue

        kind = "line"
        b = _BULLET.match(s)
        if b:
            kind, s = "item", b.group(1).strip()
        header = s.endswith(":")
        rows.append((indent + level * 2, kind, s[:-1].strip() if header else s, header))
    return rows


def _shape(entries):
    """entries: (key, value, raw_text, structured)"""
    keys = [e[0] for e in entries]
    if all(k is not None for k in keys):
        if len(set(keys)) == len(keys):
            return {e[0]: e[1] for e in entries}
        return [{e[0]: e[1]} for e in entries]
    if not any(e[0] is not None and e[3] for e in entries):
        return [e[2] for e in entries]  # plain list of strings
    return [{e[0]: e[1]} if (e[0] is not None and e[3]) else e[2] for e in entries]


def _build(rows, i, indent, items_only=False):
    entries = []
    while i < len(rows):
        ind, kind, text, header = rows[i]
        if ind < indent or (items_only and ind == indent and kind != "item"):
            break
        i += 1

        key, val = None, text
        if header:
            key, val = text, None
        else:
            m = _KV.match(text)
            if m:
                key, val = m.group(1).strip(), m.group(2).strip()

        nxt = rows[i] if i < len(rows) else None
        deeper = nxt is not None and nxt[0] > ind
        # YAML-style "Header:\n- item" where items sit at the header's indent
        flat = header and kind != "item" and nxt is not None and nxt[0] == ind and nxt[1] == "item"

        structured = header
        if deeper or flat:
            if key is None:
                key = text
            child, i = _build(rows, i, nxt[0], items_only=flat)
            val = child if val is None else {"value": val, "children": child}
            structured = True

        entries.append((key, val, text, structured))
    return _shape(entries), i


def _try_outline(s: str):
    rows = _tokenize(s)
    signals = sum(1 for r in rows if r[1] == "item" or r[3] or _KV.match(r[2]))
    if len(rows) < 2 or signals < MIN_OUTLINE_SIGNALS:
        return s, False
    value, _ = _build(rows, 0, min(r[0] for r in rows))
    return (value, True) if isinstance(value, (dict, list)) else (s, False)


# --------------------------------------------------------------------------
# The cascade
# --------------------------------------------------------------------------
# (name, parser, needs_multiline). Order = priority. Add your own here.
PARSERS: list[tuple[str, Callable[[str], tuple[Any, bool]], bool]] = [
    ("json", _try_json, False),
    ("xml", _try_xml, False),
    ("yaml", _try_yaml, True),
    ("outline", _try_outline, True),
]


def _parse_string(text: str, top: bool):
    s = _strip_fences(text)
    if not s.strip():
        return text, False
    multiline = "\n" in s
    flow = s.lstrip()[:1] in ("{", "[")

    for name, parser, needs_multiline in PARSERS:
        # Nested single-line strings are usually plain values ("Runner: x"), so only
        # JSON/XML/flow-style are attempted on them. Top-level input gets every parser.
        if needs_multiline and not (multiline or top or flow):
            continue
        try:
            parsed, ok = parser(s)
        except Exception as e:  # bad YAML/XML etc. -> try the next parser
            logger.debug(f"[cascade] {name} failed: {e}")
            continue
        if ok:
            logger.debug(f"[cascade] parsed as {name}")
            return parsed, True
    return text, False


def cascade(value: Any, depth: int = 0) -> Any:
    """Recursively turn any structured text found inside `value` into JSON-safe data."""
    if depth > MAX_DEPTH:
        return value
    if isinstance(value, dict):
        return {str(k): cascade(v, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [cascade(v, depth + 1) for v in value]
    if isinstance(value, str):
        parsed, ok = _parse_string(value, top=(depth == 0))
        if ok:
            return cascade(_to_jsonable(parsed), depth + 1)
        return value
    return value


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def serialize_agent_response(response: Any, parse_text: bool = True) -> dict[str, Any]:
    if response is None:
        return {}

    if isinstance(response, (bytes, bytearray)):
        response = response.decode("utf-8", errors="replace")

    result = _to_jsonable(response)
    if parse_text:
        result = cascade(result)

    return result if isinstance(result, dict) else {"result": result}


def serialize_agent_response_json(response: Any, **kwargs) -> str:
    return json.dumps(serialize_agent_response(response, **kwargs), indent=2, ensure_ascii=False)

def format_result_for_email(result: Any) -> str:
    if result is None:
        return "No result available"

    if isinstance(result, dict):
        return json.dumps(result, indent=2, ensure_ascii=False)

    if isinstance(result, list):
        lines = []
        for item in result:
            if isinstance(item, (dict, list)):
                nested = json.dumps(item, indent=2, ensure_ascii=False)
                lines.append("- " + nested.replace("\n", "\n  "))
            else:
                lines.append(f"- {str(item).strip()}")
        return "\n".join(lines)

    return str(result).strip()
