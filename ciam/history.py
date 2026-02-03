"""Command history tracking and replay."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Prevent circular import by importing at function level when needed


class HistoryManager:
    """Manages command history in ~/.ciam-cli-history.jsonl."""

    HISTORY_FILENAME = ".ciam-cli-history.jsonl"

    def __init__(self):
        self.history_path = Path.home() / self.HISTORY_FILENAME

    def add_entry(
        self,
        argv: List[str],
        region: Optional[str],
        env: Optional[str],
        store_id: Optional[str],
    ) -> None:
        """Add a command entry to history."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "argv": argv,
            "region": region,
            "env": env,
            "store_id": store_id,
        }

        with open(self.history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get last N history entries."""
        if not self.history_path.exists():
            return []

        entries = []
        with open(self.history_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Return last 'limit' entries
        return entries[-limit:]

    def format_history(self, entries: List[Dict[str, Any]]) -> str:
        """Format history entries for display."""
        if not entries:
            return "No history available."

        lines = ["Command History:"]
        for i, entry in enumerate(entries):
            idx = len(entries) - i - 1  # Display in reverse order
            timestamp = entry.get("timestamp", "?")
            argv = " ".join(entry.get("argv", []))
            lines.append(f"  [{idx}] {timestamp} | {argv}")

        return "\n".join(lines)

    def get_command_by_index(self, index: int, limit: int = 10) -> Optional[List[str]]:
        """Get a command by its display index."""
        history = self.get_history(limit)
        if not history:
            return None

        # Index is from the end
        actual_idx = len(history) - index - 1
        if actual_idx < 0 or actual_idx >= len(history):
            return None

        return history[actual_idx].get("argv")

    def replay_command(self, index: int, limit: int = 10) -> None:
        """
        Re-run a command by index.
        This will reinvoke the main CLI entry point.
        """
        argv = self.get_command_by_index(index, limit)
        if not argv:
            print(f"Error: Command index {index} not found in history.")
            sys.exit(1)

        print(f"Replaying: {' '.join(argv)}")
        # Remove 'ciam.py' or script name from argv if present
        if argv and argv[0] in ["ciam.py", "ciam"]:
            argv = argv[1:]

        # Import here to avoid circular imports
        from . import cli

        # Reinvoke the CLI with the saved argv
        try:
            cli.main(argv)
        except SystemExit:
            # Allow SystemExit to propagate
            raise
        except Exception as e:
            print(f"Error replaying command: {e}")
            sys.exit(1)
