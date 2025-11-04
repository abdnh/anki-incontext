from __future__ import annotations

from collections.abc import Iterable


def qt_key_to_js(key: str) -> list[str]:
    if not key.strip():
        return []
    parts = []
    for k in key.split("+"):
        if k.lower() == "ctrl":
            parts.append("Control")
        else:
            parts.append(k)
    return parts


def js_key_to_qt(keys: Iterable[str]) -> str:
    parts = []
    for k in keys:
        if k.lower() == "control":
            parts.append("Ctrl")
        else:
            parts.append(k)
    return "+".join(parts)
