"""Output logging to timestamped JSON files."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .util import redact_secrets


class OutputLogger:
    """Logs API requests/responses to timestamped JSON files."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.entries = []
        # Use current working directory for output files
        self.output_dir = Path.cwd()

    def log_entry(
        self,
        operation: str,
        request: Optional[Dict[str, Any]] = None,
        response: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Log a single API operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": operation,
        }

        if request:
            # Redact secrets from request
            entry["request"] = redact_secrets(request, self.verbose)

        if response:
            # Redact secrets from response
            entry["response"] = redact_secrets(response, self.verbose)

        if error:
            entry["error"] = error

        self.entries.append(entry)

    def write_to_file(self) -> Optional[str]:
        """Write all logged entries to timestamped JSON file."""
        if not self.entries:
            return None

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"output-{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def clear(self) -> None:
        """Clear logged entries."""
        self.entries = []


# Global logger instance
_logger: Optional[OutputLogger] = None


def get_logger(verbose: bool = False) -> OutputLogger:
    """Get or create the global logger."""
    global _logger
    if _logger is None:
        _logger = OutputLogger(verbose)
    return _logger


def reset_logger() -> None:
    """Reset the global logger (for testing)."""
    global _logger
    _logger = None
