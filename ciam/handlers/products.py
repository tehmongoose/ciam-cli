"""Products domain object handler."""

from typing import List, Optional

from ..http import APIClient
from ..util import format_operation_end, format_operation_start, format_step


def list_products(
    client: APIClient, filters: Optional[dict] = None
) -> dict:
    """List products - Not supported yet."""
    print(format_operation_start("list products"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("list products", success=False))
    return {"success": False, "message": "Not supported at this time"}


def get_product(
    client: APIClient, product_ids: List[str], verbose: bool = False
) -> dict:
    """Get one or more products by ID."""
    print(format_operation_start("get products"))

    results = []
    errors = []

    for product_id in product_ids:
        try:
            print(format_step(f"Fetching product: {product_id}", indent=2))
            # TODO: Confirm exact endpoint path
            response = client.get(f"/products/{product_id}")

            if response.get("success"):
                product_data = response.get("data", {})
                results.append(product_data)

                # Print summary
                product_name = product_data.get("name", "N/A")
                print(
                    format_step(
                        f"✓ Retrieved product {product_id}: {product_name}",
                        indent=4,
                    )
                )

                if verbose:
                    product_sku = product_data.get("sku", "")
                    if product_sku:
                        print(format_step(f"SKU: {product_sku}", indent=4))

            else:
                errors.append(f"Product {product_id}: Failed to retrieve")

        except Exception as e:
            error_msg = str(e)
            errors.append(f"Product {product_id}: {error_msg}")
            if verbose:
                print(format_step(f"Error: {error_msg}", indent=4))

    # Final summary
    print(
        format_step(
            f"Retrieved {len(results)} product(s), {len(errors)} error(s)",
            indent=2,
        )
    )

    success = len(errors) == 0
    print(format_operation_end("get products", success=success))

    return {
        "success": success,
        "products": results,
        "errors": errors,
    }


def create_product(
    client: APIClient, product_data: dict, verbose: bool = False
) -> dict:
    """Create a product - Not supported yet."""
    print(format_operation_start("create product"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("create product", success=False))
    return {"success": False, "message": "Not supported at this time"}


def update_product(
    client: APIClient, product_id: str, updates: dict, verbose: bool = False
) -> dict:
    """Update a product - Not supported yet."""
    print(format_operation_start("update product"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("update product", success=False))
    return {"success": False, "message": "Not supported at this time"}


def delete_product(
    client: APIClient, product_id: str, verbose: bool = False
) -> dict:
    """Delete a product - Not supported yet."""
    print(format_operation_start("delete product"))
    print(format_step("Not supported at this time", indent=2))
    print(format_operation_end("delete product", success=False))
    return {"success": False, "message": "Not supported at this time"}
