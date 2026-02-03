"""Clients domain object handler (future support)."""

from typing import List, Optional

from ..http import APIClient
from ..util import format_operation_end, format_operation_start, format_step


def list_clients(
    client: APIClient, filters: Optional[dict] = None
) -> dict:
    """List clients - Not supported yet."""
    print(format_operation_start("list clients"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("list clients", success=False))
    return {"success": False, "message": "Not supported at this time"}


def get_client(
    client: APIClient, client_ids: List[str], verbose: bool = False
) -> dict:
    """Get one or more clients by ID - Not supported yet."""
    print(format_operation_start("get clients"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("get clients", success=False))
    return {"success": False, "message": "Not supported at this time"}


def create_client(
    client: APIClient, client_data: dict, verbose: bool = False
) -> dict:
    """Create a client - Not supported yet."""
    print(format_operation_start("create client"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("create client", success=False))
    return {"success": False, "message": "Not supported at this time"}


def update_client(
    client: APIClient, client_id: str, updates: dict, verbose: bool = False
) -> dict:
    """Update a client - Not supported yet."""
    print(format_operation_start("update client"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("update client", success=False))
    return {"success": False, "message": "Not supported at this time"}


def delete_client(
    client: APIClient, client_id: str, verbose: bool = False
) -> dict:
    """Delete a client - Not supported yet."""
    print(format_operation_start("delete client"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("delete client", success=False))
    return {"success": False, "message": "Not supported at this time"}
