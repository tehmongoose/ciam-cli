"""Users domain object handler."""

import json
from pathlib import Path
from typing import List, Optional

from ..http import APIClient
from ..output import get_logger
from ..util import format_operation_end, format_operation_start, format_step


def list_users(
    client: APIClient, filters: Optional[dict] = None
) -> dict:
    """List users - Not supported yet."""
    print(format_operation_start("list users"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("list users", success=False))
    return {"success": False, "message": "Not supported at this time"}


def get_user(client: APIClient, user_ids: List[str], verbose: bool = False) -> dict:
    """Get one or more users by ID."""
    print(format_operation_start("get users"))

    results = []
    errors = []

    for user_id in user_ids:
        try:
            print(format_step(f"Fetching user: {user_id}", indent=2))
            # TODO: Confirm exact endpoint path
            response = client.get(f"/users/{user_id}")

            if response.get("success"):
                user_data = response.get("data", {})
                results.append(user_data)

                # Print summary
                user_email = user_data.get("email", "N/A")
                user_name = user_data.get("name", "N/A")
                print(
                    format_step(
                        f"✓ Retrieved user {user_id}: {user_email}",
                        indent=4,
                    )
                )

                if verbose:
                    print(format_step(f"Details: {user_name}", indent=4))

            else:
                errors.append(f"User {user_id}: Failed to retrieve")

        except Exception as e:
            error_msg = str(e)
            errors.append(f"User {user_id}: {error_msg}")
            if verbose:
                print(format_step(f"Error: {error_msg}", indent=4))

    # Final summary
    print(
        format_step(
            f"Retrieved {len(results)} user(s), {len(errors)} error(s)",
            indent=2,
        )
    )

    success = len(errors) == 0
    print(format_operation_end("get users", success=success))

    return {
        "success": success,
        "users": results,
        "errors": errors,
    }


def create_user(
    client: APIClient, user_data: dict, verbose: bool = False
) -> dict:
    """Create a user - Not supported yet."""
    print(format_operation_start("create user"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("create user", success=False))
    return {"success": False, "message": "Not supported at this time"}


def update_user(
    client: APIClient, user_id: str, updates: dict, verbose: bool = False
) -> dict:
    """Update a user - Not supported yet."""
    print(format_operation_start("update user"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("update user", success=False))
    return {"success": False, "message": "Not supported at this time"}


def delete_user(
    client: APIClient, user_id: str, verbose: bool = False
) -> dict:
    """Delete a user - Not supported yet."""
    print(format_operation_start("delete user"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("delete user", success=False))
    return {"success": False, "message": "Not supported at this time"}


def import_users(
    client: APIClient, file_paths: List[str], verbose: bool = False
) -> dict:
    """Import users from JSON file(s)."""
    print(format_operation_start("import users"))

    logger = get_logger(verbose)
    all_users = []
    errors = []

    for file_path in file_paths:
        try:
            print(format_step(f"Parsing file: {file_path}", indent=2))

            path = Path(file_path)
            if not path.exists():
                error_msg = f"File not found: {file_path}"
                errors.append(error_msg)
                print(format_step(f"✗ {error_msg}", indent=4))
                continue

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate schema
            if not isinstance(data, dict):
                error_msg = "File must contain a JSON object"
                errors.append(error_msg)
                print(format_step(f"✗ {error_msg}", indent=4))
                continue

            file_type = data.get("type")
            if file_type != "users":
                error_msg = f"Expected type 'users', got '{file_type}'"
                errors.append(error_msg)
                print(format_step(f"✗ {error_msg}", indent=4))
                continue

            users = data.get("users", [])
            if not isinstance(users, list):
                error_msg = "Field 'users' must be an array"
                errors.append(error_msg)
                print(format_step(f"✗ {error_msg}", indent=4))
                continue

            print(format_step(f"Found {len(users)} user(s)", indent=4))
            all_users.extend(users)

            # Log the file content
            logger.log_entry(
                operation=f"import users from {path.name}",
                request={"file": file_path},
                response={"users_count": len(users)},
            )

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {file_path}: {e}"
            errors.append(error_msg)
            print(format_step(f"✗ {error_msg}", indent=4))
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            errors.append(error_msg)
            print(format_step(f"✗ {error_msg}", indent=4))

    # Summary
    print(
        format_step(
            f"Parsed {len(all_users)} total user(s) from {len(file_paths)} file(s)",
            indent=2,
        )
    )

    if all_users:
        print(format_step("Would import to CIAM (not yet supported)", indent=2))

    success = len(errors) == 0
    print(format_operation_end("import users", success=success))

    return {
        "success": success,
        "users_parsed": len(all_users),
        "users": all_users,
        "errors": errors,
    }
