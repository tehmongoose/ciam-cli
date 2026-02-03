"""Configuration management for CIAM CLI."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from .util import format_table


class ConfigManager:
    """Manages CIAM CLI configuration in ~/.config-ciam-cli."""

    CONFIG_FILENAME = ".config-ciam-cli"
    VALID_REGIONS = ["us", "uk", "can", "anz"]
    VALID_ENVS = ["dev", "qa", "uat", "prod"]

    def __init__(self):
        self.config_path = Path.home() / self.CONFIG_FILENAME
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Optional[str]]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return {"region": None, "env": None, "store_id": None}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"region": None, "env": None, "store_id": None}

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def set_config(
        self,
        region: Optional[str] = None,
        env: Optional[str] = None,
        store_id: Optional[str] = None,
    ) -> None:
        """Set configuration values."""
        if region is not None:
            if region not in self.VALID_REGIONS:
                raise ValueError(
                    f"Invalid region '{region}'. "
                    f"Valid options: {', '.join(self.VALID_REGIONS)}"
                )
            self.config["region"] = region

        if env is not None:
            if env not in self.VALID_ENVS:
                raise ValueError(
                    f"Invalid env '{env}'. "
                    f"Valid options: {', '.join(self.VALID_ENVS)}"
                )
            self.config["env"] = env

        if store_id is not None:
            self.config["store_id"] = store_id

        self._save_config()

    def get_region(self) -> Optional[str]:
        """Get configured region."""
        return self.config.get("region")

    def get_env(self) -> Optional[str]:
        """Get configured environment."""
        return self.config.get("env")

    def get_store_id(self) -> Optional[str]:
        """Get configured default store ID."""
        return self.config.get("store_id")

    def get_config(self) -> Dict[str, Optional[str]]:
        """Get full configuration."""
        return self.config.copy()

    def validate_region_and_env(self) -> Tuple[str, str]:
        """
        Validate that region and env are set.
        Returns tuple of (region, env) or raises ValueError.
        """
        region = self.get_region()
        env = self.get_env()

        if not region or not env:
            raise ValueError(
                "Region and environment must be configured. "
                "Use: ciam.py config use --region <region> --env <env>"
            )

        return region, env

    def pretty_print(self) -> str:
        """Return formatted config display."""
        region = self.get_region() or "(not set)"
        env = self.get_env() or "(not set)"
        store_id = self.get_store_id() or "(not set)"

        lines = [
            "Current Configuration:",
            f"  Region:   {region}",
            f"  Env:      {env}",
            f"  Store ID: {store_id}",
        ]
        return "\n".join(lines)

    def print_valid_options(self) -> str:
        """Print valid regions and environments."""
        lines = [
            "Valid Regions: " + ", ".join(self.VALID_REGIONS),
            "Valid Envs:    " + ", ".join(self.VALID_ENVS),
            "",
            self.pretty_print(),
        ]
        return "\n".join(lines)
