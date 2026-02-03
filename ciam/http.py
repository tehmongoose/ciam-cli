"""HTTP client wrapper for CIAM API calls."""

from typing import Any, Dict, Optional

import requests

from .auth import get_token_manager
from .output import get_logger


class APIClient:
    """HTTP client for CIAM API calls."""

    # TODO: Replace with real CIAM base URLs
    BASE_URLS = {
        ("us", "dev"): "https://ciam-us-dev.example.com/api/v1",
        ("us", "qa"): "https://ciam-us-qa.example.com/api/v1",
        ("us", "uat"): "https://ciam-us-uat.example.com/api/v1",
        ("us", "prod"): "https://ciam-us.example.com/api/v1",
        ("uk", "dev"): "https://ciam-uk-dev.example.com/api/v1",
        ("uk", "qa"): "https://ciam-uk-qa.example.com/api/v1",
        ("uk", "uat"): "https://ciam-uk-uat.example.com/api/v1",
        ("uk", "prod"): "https://ciam-uk.example.com/api/v1",
        ("can", "dev"): "https://ciam-can-dev.example.com/api/v1",
        ("can", "qa"): "https://ciam-can-qa.example.com/api/v1",
        ("can", "uat"): "https://ciam-can-uat.example.com/api/v1",
        ("can", "prod"): "https://ciam-can.example.com/api/v1",
        ("anz", "dev"): "https://ciam-anz-dev.example.com/api/v1",
        ("anz", "qa"): "https://ciam-anz-qa.example.com/api/v1",
        ("anz", "uat"): "https://ciam-anz-uat.example.com/api/v1",
        ("anz", "prod"): "https://ciam-anz.example.com/api/v1",
    }

    def __init__(
        self,
        region: str,
        env: str,
        store_id: Optional[str] = None,
        credential_type: str = "general",
        verbose: bool = False,
    ):
        self.region = region
        self.env = env
        self.store_id = store_id
        self.credential_type = credential_type
        self.verbose = verbose
        self.token_manager = get_token_manager()
        self.logger = get_logger(verbose)

    def _get_base_url(self) -> str:
        """Get base URL for the configured region/env."""
        url = self.BASE_URLS.get((self.region, self.env))
        if not url:
            raise ValueError(
                f"Base URL not found for region '{self.region}' and env '{self.env}'"
            )
        return url

    def _get_headers(self, needs_store_header: bool = True) -> Dict[str, str]:
        """Build request headers."""
        # TokenManager.get_token signature is get_token(kind, region, env)
        kind = self.credential_type if self.credential_type != "client" else "clientops"
        token = self.token_manager.get_token(kind, self.region, self.env)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Add store header if needed and store_id is provided
        if needs_store_header and self.store_id:
            headers["X-Store-Id"] = self.store_id

        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        needs_store_header: bool = True,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the CIAM API.
        Logs the request and response to the output logger.
        """
        base_url = self._get_base_url()
        url = f"{base_url}{endpoint}"
        headers = self._get_headers(needs_store_header)

        # Prepare request metadata for logging
        request_meta = {
            "method": method,
            "url": url,
            "headers": headers.copy(),
            "params": params,
            "body": json_body,
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30,
            )

            # Prepare response metadata for logging
            response_meta = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }

            try:
                response_meta["body"] = response.json()
            except:
                response_meta["body"] = response.text

            # Log to output file
            self.logger.log_entry(
                operation=f"{method} {endpoint}",
                request=request_meta,
                response=response_meta,
            )

            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response_meta.get("body", {}),
            }

        except requests.RequestException as e:
            error_msg = str(e)
            self.logger.log_entry(
                operation=f"{method} {endpoint}",
                request=request_meta,
                error=error_msg,
            )
            raise

    def get(
        self,
        endpoint: str,
        needs_store_header: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """GET request."""
        return self._make_request(
            "GET", endpoint, needs_store_header, params=params
        )

    def post(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        needs_store_header: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST request."""
        return self._make_request(
            "POST", endpoint, needs_store_header, params=params, json_body=body
        )

    def put(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        needs_store_header: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """PUT request."""
        return self._make_request(
            "PUT", endpoint, needs_store_header, params=params, json_body=body
        )

    def patch(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        needs_store_header: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """PATCH request."""
        return self._make_request(
            "PATCH", endpoint, needs_store_header, params=params, json_body=body
        )

    def delete(
        self,
        endpoint: str,
        needs_store_header: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """DELETE request."""
        return self._make_request(
            "DELETE", endpoint, needs_store_header, params=params
        )
