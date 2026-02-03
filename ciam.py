#!/usr/bin/env python3
"""CIAM CLI - Command-line interface for PingOne-based identity management."""

import sys

from ciam.cli import main

if __name__ == "__main__":
    # Activate argcomplete for tab completion support
    try:
        import argcomplete
        argcomplete.autocomplete  # Reference to check it exists
    except ImportError:
        # argcomplete not installed; continue without completion
        pass

    main()
