"""Authentication and token management for PingOne OAuth2."""

import base64
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Literal, Tuple

import requests
from dotenv import load_dotenv

from .output import get_logger

# Load environment variables from .env
load_dotenv()


# Static mapping for token endpoints (placeholders)
PINGONE_TOKEN_URLS: Dict[Tuple[str, str], str] = {
    ("us", "dev"): "https://auth-us-dev.pingone.com/oauth2/token",
    ("us", "qa"): "https://auth-us-qa.pingone.com/oauth2/token",
    ("us", "uat"): "https://auth-us-uat.pingone.com/oauth2/token",
    ("us", "prod"): "https://auth-us.pingone.com/oauth2/token",
    ("uk", "qa"): "https://auth-uk-qa.pingone.com/oauth2/token",
    ("uk", "uat"): "https://auth-uk-uat.pingone.com/oauth2/token",
    ("uk", "prod"): "https://auth-uk.pingone.com/oauth2/token",
    ("can", "qa"): "https://auth-can-qa.pingone.com/oauth2/token",
    ("can", "uat"): "https://auth-can-uat.pingone.com/oauth2/token",
    ("can", "prod"): "https://auth-can.pingone.com/oauth2/token",
    ("anz", "qa"): "https://auth-anz-qa.pingone.com/oauth2/token",
    ("anz", "uat"): "https://auth-anz-uat.pingone.com/oauth2/token",
    ("anz", "prod"): "https://auth-anz.pingone.com/oauth2/token",
}


class TokenManager:
    """Manages OAuth2 tokens from PingOne.

    Supports two request methods:
      - general: Authorization: Basic <base64(client_id:client_secret)> and form body grant_type only
      - clientops: form body includes client_id and client_secret (no Authorization header)
    """

    def __init__(self) -> None:
        # tokens stored with keys: "general" and "clientops"
        self.tokens: Dict[str, Optional[Dict]] = {"general": None, "clientops": None}

    def _get_credential_env_var(self, region: str, env: str, kind: Literal["general", "clientops"]) -> Tuple[Optional[str], Optional[str]]:
        prefix = f"{region.upper()}_{env.upper()}"
        if kind == "general":
            suffix = "GENERAL"
        else:
            suffix = "CLIENTOPS"

        client_id = os.getenv(f"{prefix}_{suffix}_CLIENT_ID")
        client_secret = os.getenv(f"{prefix}_{suffix}_CLIENT_SECRET")
        return client_id, client_secret

    # -- Helper methods to prepare request metadata for testing --
    def prepare_general_request(self, client_id: str, client_secret: str, token_url: str) -> Dict:
        """Return headers and data that would be used for a GENERAL token request."""
        creds = f"{client_id}:{client_secret}"
        basic = base64.b64encode(creds.encode()).decode()
        headers = {"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials"}
        return {"url": token_url, "headers": headers, "data": data}

    def prepare_clientops_request(self, client_id: str, client_secret: str, token_url: str) -> Dict:
        """Return headers and data that would be used for a CLIENT-OPS token request."""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}
        return {"url": token_url, "headers": headers, "data": data}

    def fetch_general_token(self, region: str, env: str) -> Dict:
        """Fetch token using Authorization: Basic and form-encoded grant_type only."""
        token_url = PINGONE_TOKEN_URLS.get((region, env))
        if not token_url:
            raise ValueError(f"Token endpoint not found for region '{region}' and env '{env}'")

        client_id, client_secret = self._get_credential_env_var(region, env, "general")
        if not client_id or not client_secret:
            raise ValueError(f"Missing GENERAL credentials for {region}/{env}; set env vars")

        logger = get_logger(verbose=False)

        # prepare request
        req = self.prepare_general_request(client_id, client_secret, token_url)

        # Log request (logger will redact secrets)
        logger.log_entry(operation="token_request:general", request={"method": "POST", "url": req["url"], "headers": req["headers"], "body": req["data"]})

        try:
            resp = requests.post(req["url"], headers=req["headers"], data=req["data"], timeout=10)
            try:
                body = resp.json()
            except Exception:
                body = resp.text

            response_meta = {"status_code": resp.status_code, "headers": dict(resp.headers), "body": body}
            logger.log_entry(operation="token_response:general", response=response_meta)

            if resp.status_code != 200:
                raise RuntimeError(f"Failed to fetch GENERAL token: {resp.status_code} {resp.text}")

            return body
        except requests.RequestException as e:
            logger.log_entry(operation="token_response:general", error=str(e))
            raise RuntimeError(f"Failed to retrieve GENERAL token: {e}")

    def fetch_clientops_token(self, region: str, env: str) -> Dict:
        """Fetch token by posting client_id and client_secret in form body (no Authorization header)."""
        token_url = PINGONE_TOKEN_URLS.get((region, env))
        if not token_url:
            raise ValueError(f"Token endpoint not found for region '{region}' and env '{env}'")

        client_id, client_secret = self._get_credential_env_var(region, env, "clientops")
        if not client_id or not client_secret:
            raise ValueError(f"Missing CLIENTOPS credentials for {region}/{env}; set env vars")

        logger = get_logger(verbose=False)

        req = self.prepare_clientops_request(client_id, client_secret, token_url)
        logger.log_entry(operation="token_request:clientops", request={"method": "POST", "url": req["url"], "headers": req["headers"], "body": req["data"]})

        try:
            resp = requests.post(req["url"], headers=req["headers"], data=req["data"], timeout=10)
            try:
                body = resp.json()
            except Exception:
                body = resp.text

            response_meta = {"status_code": resp.status_code, "headers": dict(resp.headers), "body": body}
            logger.log_entry(operation="token_response:clientops", response=response_meta)

            if resp.status_code != 200:
                raise RuntimeError(f"Failed to fetch CLIENTOPS token: {resp.status_code} {resp.text}")

            return body
        except requests.RequestException as e:
            logger.log_entry(operation="token_response:clientops", error=str(e))
            raise RuntimeError(f"Failed to retrieve CLIENTOPS token: {e}")

    def get_token(self, kind: Literal["general", "clientops"], region: str, env: str, force_refresh: bool = False) -> str:
        """Public method to get token by kind using cache."""
        # Normalize kind
        if kind not in ("general", "clientops"):
            if kind == "client":
                kind = "clientops"
            else:
                raise ValueError(f"Unknown token kind: {kind}")

        # Check cache
        token_data = self.tokens.get(kind)
        if not force_refresh and token_data and token_data.get("expires_at") and token_data["expires_at"] > datetime.utcnow() + timedelta(minutes=5):
            return token_data["access_token"]

        # Fetch depending on kind
        if kind == "general":
            body = self.fetch_general_token(region, env)
        else:
            body = self.fetch_clientops_token(region, env)

        # Expect body to be JSON with access_token and expires_in
        access_token = body.get("access_token") if isinstance(body, dict) else None
        expires_in = body.get("expires_in") if isinstance(body, dict) else None

        if not access_token:
            raise RuntimeError(f"Token response did not contain access_token: {body}")

        expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in or 3600))

        # Store unredacted token info for tokens view
        # Also store client id/secret for display in tokens view
        client_id, client_secret = self._get_credential_env_var(region, env, kind)
        self.tokens[kind] = {
            "access_token": access_token,
            "expires_at": expires_at,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        return access_token

    def get_token_info(self, kind: Literal["general", "clientops"] = "general") -> Optional[Dict]:
        return self.tokens.get(kind)

    def format_token_display(self, kind: Literal["general", "clientops"] = "general") -> str:
        token_data = self.tokens.get(kind)
        if not token_data:
            return f"No {kind} token cached."

        lines = [f"{kind.upper()} Token:", f"  Access Token: {token_data['access_token']}", f"  Client ID: {token_data.get('client_id', 'N/A')}", f"  Client Secret: {token_data.get('client_secret', 'N/A')}", f"  Expires At: {token_data.get('expires_at', 'N/A')}"]
        return "\n".join(lines)

    def clear_cache(self) -> None:
        self.tokens = {"general": None, "clientops": None}


# Global token manager instance
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
