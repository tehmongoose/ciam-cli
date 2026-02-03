"""Stores domain object handler."""

from typing import List, Optional

from ..http import APIClient
from ..util import format_operation_end, format_operation_start, format_step


def list_stores(
    client: APIClient, filters: Optional[dict] = None
) -> dict:
    """List stores - Not supported yet."""
    print(format_operation_start("list stores"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("list stores", success=False))
    return {"success": False, "message": "Not supported at this time"}


def get_store(
    client: APIClient, store_ids: List[str], verbose: bool = False
) -> dict:
    """Get one or more stores by ID."""
    print(format_operation_start("get stores"))

    results = []
    errors = []

    for store_id in store_ids:
        try:
            print(format_step(f"Fetching store: {store_id}", indent=2))
            # TODO: Confirm exact endpoint path
            # NOTE: Store operations do NOT include X-Store-Id header
            response = client.get(f"/stores/{store_id}", needs_store_header=False)

            if response.get("success"):
                store_data = response.get("data", {})
                results.append(store_data)

                # Print summary
                store_name = store_data.get("name", "N/A")
                print(
                    format_step(
                        f"✓ Retrieved store {store_id}: {store_name}",
                        indent=4,
                    )
                )

                if verbose:
                    store_type = store_data.get("type", "")
                    if store_type:
                        print(format_step(f"Type: {store_type}", indent=4))

            else:
                errors.append(f"Store {store_id}: Failed to retrieve")

        except Exception as e:
            error_msg = str(e)
            errors.append(f"Store {store_id}: {error_msg}")
            if verbose:
                print(format_step(f"Error: {error_msg}", indent=4))

    # Final summary
    print(
        format_step(
            f"Retrieved {len(results)} store(s), {len(errors)} error(s)",
            indent=2,
        )
    )

    success = len(errors) == 0
    print(format_operation_end("get stores", success=success))

    return {
        "success": success,
        "stores": results,
        "errors": errors,
    }


def create_store(
    client: APIClient, store_data: dict, verbose: bool = False
) -> dict:
    """Create a store - Not supported yet."""
    print(format_operation_start("create store"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("create store", success=False))
    return {"success": False, "message": "Not supported at this time"}


def update_store(
    client: APIClient, store_id: str, updates: dict, verbose: bool = False
) -> dict:
    """Update a store - Not supported yet."""
    print(format_operation_start("update store"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("update store", success=False))
    return {"success": False, "message": "Not supported at this time"}


def delete_store(
    client: APIClient, store_id: str, verbose: bool = False
) -> dict:
    """Delete a store - Not supported yet."""
    print(format_operation_start("delete store"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("delete store", success=False))
    return {"success": False, "message": "Not supported at this time"}


def apply_store(
    client: APIClient, store_id: str, updates: dict, verbose: bool = False
) -> dict:
    """
    Apply (idempotent update) a store - Not supported yet.
    Intended behavior: merge provided fields with existing store config.
    """
    print(format_operation_start("apply store"))
    print(format_step("Not supported at this time", indent=2))
    print(
        format_step(
            "Intended behavior: merge configuration with existing store",
            indent=2,
        )
    )
    print(format_operation_end("apply store", success=False))
    return {"success": False, "message": "Not supported at this time"}


def diff_store(
    client: APIClient, store_id: str, updates: dict, verbose: bool = False
) -> dict:
    """
    Show diff of what would be applied to a store - Not supported yet.
    Intended behavior: compare provided fields against current store config.
    """
    print(format_operation_start("diff store"))
    print(format_step("Not supported at this time", indent=2))
    print(
        format_step(
            "Intended behavior: show diff of changes that would be applied",
            indent=2,
        )
    )
    print(format_operation_end("diff store", success=False))
    return {"success": False, "message": "Not supported at this time"}
