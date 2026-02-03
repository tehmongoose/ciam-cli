"""Shared formatting and utility helpers."""

import json
import re
import sys
from typing import Any, Dict, Optional

# Ensure stdout can handle Unicode on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass


def redact_secrets(data: Any, verbose: bool = False) -> Any:
    """
    Recursively redact sensitive fields from data structures.
    If verbose=True, only redact passwords and secrets, leave tokens visible.
    If verbose=False, redact tokens, passwords, secrets, keys, etc.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            key_lower = key.lower()
            # Always redact these
            if any(
                x in key_lower
                for x in ["password", "secret", "authorization", "bearer"]
            ):
                result[key] = "***REDACTED***"
            # In non-verbose mode, redact tokens and keys
            elif not verbose and any(
                x in key_lower for x in ["token", "key", "credential", "access"]
            ):
                result[key] = "***REDACTED***"
            else:
                result[key] = redact_secrets(value, verbose)
        return result
    elif isinstance(data, list):
        return [redact_secrets(item, verbose) for item in data]
    else:
        return data


def format_operation_start(title: str) -> str:
    """Format operation start marker."""
    return f"▼ {title}"


def format_operation_end(title: str, success: bool = True) -> str:
    """Format operation end marker."""
    status = "success" if success else "failure"
    return f"▲ {title} ({status})"


def format_step(message: str, indent: int = 2) -> str:
    """Format a step within an operation."""
    prefix = " " * indent
    return f"{prefix}• {message}"


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format simple table output."""
    if not rows:
        return ""

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    lines = []
    # Header
    header_line = " | ".join(
        h.ljust(col_widths[i]) for i, h in enumerate(headers)
    )
    lines.append(header_line)
    lines.append("-" * len(header_line))

    # Rows
    for row in rows:
        row_line = " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        )
        lines.append(row_line)

    return "\n".join(lines)


def format_json_compact(data: Any) -> str:
    """Format JSON compactly on a single line (for terminal display)."""
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def format_json_pretty(data: Any) -> str:
    """Format JSON with indentation (for display and files)."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def safe_get_nested(data: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """
    Safely get nested dict value using dot notation.
    E.g., "user.profile.email"
    """
    for key in keys.split("."):
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return default
    return data if data is not None else default


def mask_token_for_display(token: str, visible_chars: int = 10) -> str:
    """Mask a token/secret for display, showing only first and last N chars."""
    if len(token) <= visible_chars * 2:
        return token
    return f"{token[:visible_chars]}...{token[-visible_chars:]}"
