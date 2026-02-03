"""Groups domain object handler."""

from typing import List, Optional

from ..http import APIClient
from ..util import format_operation_end, format_operation_start, format_step


def list_groups(
    client: APIClient, filters: Optional[dict] = None
) -> dict:
    """List groups - Not supported yet."""
    print(format_operation_start("list groups"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("list groups", success=False))
    return {"success": False, "message": "Not supported at this time"}


def get_group(
    client: APIClient, group_ids: List[str], verbose: bool = False
) -> dict:
    """Get one or more groups by ID."""
    print(format_operation_start("get groups"))

    results = []
    errors = []

    for group_id in group_ids:
        try:
            print(format_step(f"Fetching group: {group_id}", indent=2))
            # TODO: Confirm exact endpoint path
            response = client.get(f"/groups/{group_id}")

            if response.get("success"):
                group_data = response.get("data", {})
                results.append(group_data)

                # Print summary
                group_name = group_data.get("name", "N/A")
                print(
                    format_step(
                        f"✓ Retrieved group {group_id}: {group_name}",
                        indent=4,
                    )
                )

                if verbose:
                    group_desc = group_data.get("description", "")
                    if group_desc:
                        print(format_step(f"Description: {group_desc}", indent=4))

            else:
                errors.append(f"Group {group_id}: Failed to retrieve")

        except Exception as e:
            error_msg = str(e)
            errors.append(f"Group {group_id}: {error_msg}")
            if verbose:
                print(format_step(f"Error: {error_msg}", indent=4))

    # Final summary
    print(
        format_step(
            f"Retrieved {len(results)} group(s), {len(errors)} error(s)",
            indent=2,
        )
    )

    success = len(errors) == 0
    print(format_operation_end("get groups", success=success))

    return {
        "success": success,
        "groups": results,
        "errors": errors,
    }


def create_group(
    client: APIClient, group_data: dict, verbose: bool = False
) -> dict:
    """Create a group - Not supported yet."""
    print(format_operation_start("create group"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("create group", success=False))
    return {"success": False, "message": "Not supported at this time"}


def update_group(
    client: APIClient, group_id: str, updates: dict, verbose: bool = False
) -> dict:
    """Update a group - Not supported yet."""
    print(format_operation_start("update group"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("update group", success=False))
    return {"success": False, "message": "Not supported at this time"}


def delete_group(
    client: APIClient, group_id: str, verbose: bool = False
) -> dict:
    """Delete a group - Not supported yet."""
    print(format_operation_start("delete group"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("delete group", success=False))
    return {"success": False, "message": "Not supported at this time"}
