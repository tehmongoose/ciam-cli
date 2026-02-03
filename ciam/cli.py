"""Command-line interface with argparse."""

import argparse
import sys
from typing import Optional

from .auth import get_token_manager
from .completion import (
    generate_bash_completion_script,
    generate_powershell_completion_script,
    generate_zsh_completion_script,
)
from .config import ConfigManager
from .handlers import groups, orgs, products, stores, users, clients
from .history import HistoryManager
from .http import APIClient
from .output import get_logger
from .util import format_operation_end, format_operation_start, format_step


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="ciam.py",
        description="CIAM CLI for PingOne-based identity management.",
    )

    # Global flags
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed operation metadata",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # ===== CONFIG =====
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(
        dest="config_action", help="Config actions"
    )

    # config use
    use_parser = config_subparsers.add_parser(
        "use", help="Set current region/environment/store"
    )
    use_parser.add_argument(
        "shorthand",
        nargs="?",
        help='Shorthand format: "us-qa" (region-env)',
    )
    use_parser.add_argument(
        "--region",
        help="Region (us, uk, can, anz)",
    )
    use_parser.add_argument(
        "--env",
        help="Environment (dev, qa, uat, prod)",
    )
    use_parser.add_argument(
        "--store-id",
        "--si",
        dest="store_id",
        help="Default store ID",
    )

    # config get
    config_subparsers.add_parser("get", help="Show current configuration")

    # config list
    config_subparsers.add_parser(
        "list", help="List valid regions/environments and current config"
    )

    # ===== TOKENS =====
    tokens_parser = subparsers.add_parser("tokens", help="Manage authentication tokens")
    tokens_subparsers = tokens_parser.add_subparsers(
        dest="tokens_action", help="Token actions"
    )
    tokens_subparsers.add_parser(
        "view", help="View current tokens (unmasked)"
    )

    # ===== USERS =====
    users_parser = subparsers.add_parser("users", help="Manage users")
    users_subparsers = users_parser.add_subparsers(
        dest="users_action", help="User actions"
    )

    users_list = users_subparsers.add_parser("list", help="List users")
    users_list.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    users_get = users_subparsers.add_parser("get", help="Get users by ID")
    users_get.add_argument("ids", nargs="+", help="User ID(s)")
    users_get.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    users_create = users_subparsers.add_parser("create", help="Create a user")
    users_create.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    users_update = users_subparsers.add_parser("update", help="Update a user")
    users_update.add_argument("id", help="User ID")
    users_update.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    users_delete = users_subparsers.add_parser("delete", help="Delete a user")
    users_delete.add_argument("id", help="User ID")
    users_delete.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    users_import = users_subparsers.add_parser("import", help="Import users from file(s)")
    users_import.add_argument("files", nargs="+", help="JSON file(s) to import")
    users_import.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    # ===== GROUPS =====
    groups_parser = subparsers.add_parser("groups", help="Manage groups")
    groups_subparsers = groups_parser.add_subparsers(
        dest="groups_action", help="Group actions"
    )

    groups_list = groups_subparsers.add_parser("list", help="List groups")
    groups_list.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    groups_get = groups_subparsers.add_parser("get", help="Get groups by ID")
    groups_get.add_argument("ids", nargs="+", help="Group ID(s)")
    groups_get.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    groups_create = groups_subparsers.add_parser("create", help="Create a group")
    groups_create.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    groups_update = groups_subparsers.add_parser("update", help="Update a group")
    groups_update.add_argument("id", help="Group ID")
    groups_update.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    groups_delete = groups_subparsers.add_parser("delete", help="Delete a group")
    groups_delete.add_argument("id", help="Group ID")
    groups_delete.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    # ===== ORGS =====
    orgs_parser = subparsers.add_parser("orgs", help="Manage organizations")
    orgs_subparsers = orgs_parser.add_subparsers(
        dest="orgs_action", help="Org actions"
    )

    orgs_list = orgs_subparsers.add_parser("list", help="List orgs")
    orgs_list.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    orgs_get = orgs_subparsers.add_parser("get", help="Get orgs by ID")
    orgs_get.add_argument("ids", nargs="+", help="Org ID(s)")
    orgs_get.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    orgs_create = orgs_subparsers.add_parser("create", help="Create an org")
    orgs_create.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    orgs_update = orgs_subparsers.add_parser("update", help="Update an org")
    orgs_update.add_argument("id", help="Org ID")
    orgs_update.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    orgs_delete = orgs_subparsers.add_parser("delete", help="Delete an org")
    orgs_delete.add_argument("id", help="Org ID")
    orgs_delete.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    orgs_apply = orgs_subparsers.add_parser("apply", help="Apply org config")
    orgs_apply.add_argument("id", help="Org ID")
    orgs_apply.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    orgs_diff = orgs_subparsers.add_parser("diff", help="Diff org config")
    orgs_diff.add_argument("id", help="Org ID")
    orgs_diff.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    # ===== STORES =====
    stores_parser = subparsers.add_parser("stores", help="Manage stores")
    stores_subparsers = stores_parser.add_subparsers(
        dest="stores_action", help="Store actions"
    )

    stores_list = stores_subparsers.add_parser("list", help="List stores")

    stores_get = stores_subparsers.add_parser("get", help="Get stores by ID")
    stores_get.add_argument("ids", nargs="+", help="Store ID(s)")

    stores_create = stores_subparsers.add_parser("create", help="Create a store")

    stores_update = stores_subparsers.add_parser("update", help="Update a store")
    stores_update.add_argument("id", help="Store ID")

    stores_delete = stores_subparsers.add_parser("delete", help="Delete a store")
    stores_delete.add_argument("id", help="Store ID")

    stores_apply = stores_subparsers.add_parser("apply", help="Apply store config")
    stores_apply.add_argument("id", help="Store ID")

    stores_diff = stores_subparsers.add_parser("diff", help="Diff store config")
    stores_diff.add_argument("id", help="Store ID")

    # ===== PRODUCTS =====
    products_parser = subparsers.add_parser("products", help="Manage products")
    products_subparsers = products_parser.add_subparsers(
        dest="products_action", help="Product actions"
    )

    products_list = products_subparsers.add_parser("list", help="List products")
    products_list.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    products_get = products_subparsers.add_parser("get", help="Get products by ID")
    products_get.add_argument("ids", nargs="+", help="Product ID(s)")
    products_get.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    products_create = products_subparsers.add_parser("create", help="Create a product")
    products_create.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    products_update = products_subparsers.add_parser("update", help="Update a product")
    products_update.add_argument("id", help="Product ID")
    products_update.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    products_delete = products_subparsers.add_parser("delete", help="Delete a product")
    products_delete.add_argument("id", help="Product ID")
    products_delete.add_argument("--store-id", "--si", dest="store_id", help="Store ID")

    # ===== HISTORY =====
    history_parser = subparsers.add_parser("history", help="View or replay command history")
    history_parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=10,
        help="Number of history entries to show (max 100)",
    )
    history_parser.add_argument(
        "-r",
        "--replay",
        type=int,
        help="Replay command by index",
    )

    # ===== COMPLETION =====
    completion_parser = subparsers.add_parser(
        "completion", help="Generate shell completion scripts"
    )
    completion_subparsers = completion_parser.add_subparsers(
        dest="completion_action", help="Completion actions"
    )
    completion_subparsers.add_parser("bash", help="Generate Bash completion script")
    completion_subparsers.add_parser("zsh", help="Generate Zsh completion script")
    completion_subparsers.add_parser(
        "powershell", help="Generate PowerShell completion script"
    )

    # Try to install argcomplete completers (if available) and activate
    try:
        import argcomplete
        # Install our custom completers onto the parser
        try:
            from .completion import install_completers
            install_completers(parser)
        except Exception:
            # If installing custom completers fails, continue silently
            pass

        # Activate argcomplete for this parser
        try:
            argcomplete.autocomplete(parser)
        except Exception:
            # Non-fatal if autocomplete activation fails
            pass
    except ImportError:
        # argcomplete not installed; do nothing
        pass

    return parser.parse_args(argv)


def handle_config(args: argparse.Namespace) -> None:
    """Handle config commands."""
    config = ConfigManager()

    if args.config_action == "use":
        # Parse shorthand or explicit args
        region = args.region
        env = args.env

        if args.shorthand:
            # Parse shorthand like "us-qa"
            parts = args.shorthand.split("-")
            if len(parts) == 2:
                region, env = parts
            else:
                print("Error: Invalid shorthand format. Use 'region-env' (e.g., 'us-qa')")
                sys.exit(1)

        if not region or not env:
            print("Error: Both region and environment are required")
            sys.exit(1)

        try:
            config.set_config(
                region=region,
                env=env,
                store_id=args.store_id,
            )
            print(format_operation_start("set config"))
            print(format_step(f"Region: {region}", indent=2))
            print(format_step(f"Environment: {env}", indent=2))
            if args.store_id:
                print(format_step(f"Store ID: {args.store_id}", indent=2))
            print(format_operation_end("set config"))
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.config_action == "get":
        print(config.pretty_print())

    elif args.config_action == "list":
        print(config.print_valid_options())

    else:
        print("Use: ciam.py config <get|list|use>")
        sys.exit(1)


def handle_tokens(args: argparse.Namespace) -> None:
    """Handle token commands."""
    if args.tokens_action == "view":
        print(format_operation_start("view tokens"))
        config = ConfigManager()
        region, env = config.validate_region_and_env()

        token_manager = get_token_manager()

        try:
            # Get general token
            print(format_step("Fetching general token...", indent=2))
            token_manager.get_token("general", region, env)
            print(format_step("✓ Retrieved general token", indent=4))
            print(token_manager.format_token_display("general"))
        except Exception as e:
            print(format_step(f"✗ Error: {e}", indent=4))

        print()

        try:
            # Get client token
            print(format_step("Fetching client operations token...", indent=2))
            token_manager.get_token("clientops", region, env)
            print(format_step("✓ Retrieved client operations token", indent=4))
            print(token_manager.format_token_display("clientops"))
        except Exception as e:
            print(format_step(f"✗ Error: {e}", indent=4))

        print(format_operation_end("view tokens"))
    else:
        print("Use: ciam.py tokens view")
        sys.exit(1)


def handle_users(args: argparse.Namespace) -> None:
    """Handle user commands."""
    config = ConfigManager()
    region, env = config.validate_region_and_env()

    # Determine store_id
    store_id = args.store_id if hasattr(args, "store_id") else None
    if not store_id:
        store_id = config.get_store_id()
    if not store_id:
        print("Error: Store ID is required. Provide --store-id or set default with 'config use'")
        sys.exit(1)

    client = APIClient(
        region=region,
        env=env,
        store_id=store_id,
        credential_type="general",
        verbose=args.verbose,
    )

    if args.users_action == "list":
        users.list_users(client)
    elif args.users_action == "get":
        users.get_user(client, args.ids, verbose=args.verbose)
    elif args.users_action == "create":
        users.create_user(client, {}, verbose=args.verbose)
    elif args.users_action == "update":
        users.update_user(client, args.id, {}, verbose=args.verbose)
    elif args.users_action == "delete":
        users.delete_user(client, args.id, verbose=args.verbose)
    elif args.users_action == "import":
        users.import_users(client, args.files, verbose=args.verbose)
    else:
        print("Use: ciam.py users <list|get|create|update|delete|import>")
        sys.exit(1)

    # Write output file
    logger = get_logger(args.verbose)
    output_file = logger.write_to_file()
    if output_file:
        print(f"\nOutput written to: {output_file}")


def handle_groups(args: argparse.Namespace) -> None:
    """Handle group commands."""
    config = ConfigManager()
    region, env = config.validate_region_and_env()

    store_id = args.store_id if hasattr(args, "store_id") else None
    if not store_id:
        store_id = config.get_store_id()
    if not store_id:
        print("Error: Store ID is required. Provide --store-id or set default with 'config use'")
        sys.exit(1)

    client = APIClient(
        region=region,
        env=env,
        store_id=store_id,
        credential_type="general",
        verbose=args.verbose,
    )

    if args.groups_action == "list":
        groups.list_groups(client)
    elif args.groups_action == "get":
        groups.get_group(client, args.ids, verbose=args.verbose)
    elif args.groups_action == "create":
        groups.create_group(client, {}, verbose=args.verbose)
    elif args.groups_action == "update":
        groups.update_group(client, args.id, {}, verbose=args.verbose)
    elif args.groups_action == "delete":
        groups.delete_group(client, args.id, verbose=args.verbose)
    else:
        print("Use: ciam.py groups <list|get|create|update|delete>")
        sys.exit(1)

    logger = get_logger(args.verbose)
    output_file = logger.write_to_file()
    if output_file:
        print(f"\nOutput written to: {output_file}")


def handle_orgs(args: argparse.Namespace) -> None:
    """Handle org commands."""
    config = ConfigManager()
    region, env = config.validate_region_and_env()

    store_id = args.store_id if hasattr(args, "store_id") else None
    if not store_id:
        store_id = config.get_store_id()
    if not store_id:
        print("Error: Store ID is required. Provide --store-id or set default with 'config use'")
        sys.exit(1)

    client = APIClient(
        region=region,
        env=env,
        store_id=store_id,
        credential_type="general",
        verbose=args.verbose,
    )

    if args.orgs_action == "list":
        orgs.list_orgs(client)
    elif args.orgs_action == "get":
        orgs.get_org(client, args.ids, verbose=args.verbose)
    elif args.orgs_action == "create":
        orgs.create_org(client, {}, verbose=args.verbose)
    elif args.orgs_action == "update":
        orgs.update_org(client, args.id, {}, verbose=args.verbose)
    elif args.orgs_action == "delete":
        orgs.delete_org(client, args.id, verbose=args.verbose)
    elif args.orgs_action == "apply":
        orgs.apply_org(client, args.id, {}, verbose=args.verbose)
    elif args.orgs_action == "diff":
        orgs.diff_org(client, args.id, {}, verbose=args.verbose)
    else:
        print("Use: ciam.py orgs <list|get|create|update|delete|apply|diff>")
        sys.exit(1)

    logger = get_logger(args.verbose)
    output_file = logger.write_to_file()
    if output_file:
        print(f"\nOutput written to: {output_file}")


def handle_stores(args: argparse.Namespace) -> None:
    """Handle store commands."""
    config = ConfigManager()
    region, env = config.validate_region_and_env()

    # Note: Stores don't need store_id header, but we still need region/env
    client = APIClient(
        region=region,
        env=env,
        store_id=None,
        credential_type="general",
        verbose=args.verbose,
    )

    if args.stores_action == "list":
        stores.list_stores(client)
    elif args.stores_action == "get":
        stores.get_store(client, args.ids, verbose=args.verbose)
    elif args.stores_action == "create":
        stores.create_store(client, {}, verbose=args.verbose)
    elif args.stores_action == "update":
        stores.update_store(client, args.id, {}, verbose=args.verbose)
    elif args.stores_action == "delete":
        stores.delete_store(client, args.id, verbose=args.verbose)
    elif args.stores_action == "apply":
        stores.apply_store(client, args.id, {}, verbose=args.verbose)
    elif args.stores_action == "diff":
        stores.diff_store(client, args.id, {}, verbose=args.verbose)
    else:
        print("Use: ciam.py stores <list|get|create|update|delete|apply|diff>")
        sys.exit(1)

    logger = get_logger(args.verbose)
    output_file = logger.write_to_file()
    if output_file:
        print(f"\nOutput written to: {output_file}")


def handle_products(args: argparse.Namespace) -> None:
    """Handle product commands."""
    config = ConfigManager()
    region, env = config.validate_region_and_env()

    store_id = args.store_id if hasattr(args, "store_id") else None
    if not store_id:
        store_id = config.get_store_id()
    if not store_id:
        print("Error: Store ID is required. Provide --store-id or set default with 'config use'")
        sys.exit(1)

    client = APIClient(
        region=region,
        env=env,
        store_id=store_id,
        credential_type="general",
        verbose=args.verbose,
    )

    if args.products_action == "list":
        products.list_products(client)
    elif args.products_action == "get":
        products.get_product(client, args.ids, verbose=args.verbose)
    elif args.products_action == "create":
        products.create_product(client, {}, verbose=args.verbose)
    elif args.products_action == "update":
        products.update_product(client, args.id, {}, verbose=args.verbose)
    elif args.products_action == "delete":
        products.delete_product(client, args.id, verbose=args.verbose)
    else:
        print("Use: ciam.py products <list|get|create|update|delete>")
        sys.exit(1)

    logger = get_logger(args.verbose)
    output_file = logger.write_to_file()
    if output_file:
        print(f"\nOutput written to: {output_file}")


def handle_history(args: argparse.Namespace) -> None:
    """Handle history commands."""
    history = HistoryManager()

    if hasattr(args, "replay") and args.replay is not None:
        # Replay a command
        history.replay_command(args.replay, limit=args.number)
    else:
        # Show history
        entries = history.get_history(limit=min(args.number, 100))
        print(history.format_history(entries))


def handle_completion(args: argparse.Namespace) -> None:
    """Handle completion commands."""
    if args.completion_action == "bash":
        print(generate_bash_completion_script())
    elif args.completion_action == "zsh":
        print(generate_zsh_completion_script())
    elif args.completion_action == "powershell":
        print(generate_powershell_completion_script())
    else:
        print("Use: ciam.py completion <bash|zsh|powershell>")
        sys.exit(1)


def main(argv: Optional[list] = None) -> None:
    """Main CLI entry point."""
    # Parse arguments
    try:
        args = parse_args(argv)
    except SystemExit:
        # argparse calls sys.exit on parse errors
        raise

    # Record in history
    history = HistoryManager()
    config = ConfigManager()
    region = config.get_region()
    env = config.get_env()
    store_id = config.get_store_id()

    full_argv = sys.argv[1:] if argv is None else argv
    if args.command and args.command not in ("history", "completion"):
        history.add_entry(
            argv=["ciam.py"] + full_argv,
            region=region,
            env=env,
            store_id=store_id,
        )

    # Route to handlers
    if args.command == "config":
        handle_config(args)
    elif args.command == "tokens":
        handle_tokens(args)
    elif args.command == "users":
        handle_users(args)
    elif args.command == "groups":
        handle_groups(args)
    elif args.command == "orgs":
        handle_orgs(args)
    elif args.command == "stores":
        handle_stores(args)
    elif args.command == "products":
        handle_products(args)
    elif args.command == "history":
        handle_history(args)
    elif args.command == "completion":
        handle_completion(args)
    else:
        print("Use: ciam.py <command> [options]")
        print("Available commands: config, tokens, users, groups, orgs, stores, products, history, completion")
        print("Use 'ciam.py <command> --help' for more information")
        sys.exit(1)
