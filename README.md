# CIAM CLI

A production-quality Python command-line interface for managing CIAM (Customer Identity and Access Management) platform operations via PingOne OAuth2 authentication.

## Features

- **PingOne OAuth2 Authentication**: Uses client credentials flow to obtain access tokens
- **Multi-region & Multi-environment Support**: US, UK, Canada, and ANZ regions; Dev, QA, UAT, and Prod environments
- **Modular Domain Handlers**: Support for Users, Groups, Organizations, Stores, Products, and Clients
- **Configuration Management**: Persistent configuration stored in `~/.config-ciam-cli`
- **Command History**: Track and replay previous commands
- **Timestamped JSON Logging**: All API requests and responses logged to `output-<timestamp>.json`
- **Verbose Mode**: Detailed operation metadata and step-by-step output
- **Secret Redaction**: Automatic masking of sensitive credentials in logs (except in `tokens view`)
- **Human-Friendly Terminal Output**: Clear operation framing with `▼`/`▲` markers and indented steps

## Installation

### Prerequisites

- Python 3.11+
- pip or conda

### Setup

1. Clone or download the project:
```bash
cd ciam-cli
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your PingOne client credentials
nano .env  # or edit with your preferred editor
```

## Configuration

### Setup Current Region & Environment

Before running most commands, configure your current region and environment:

```bash

# Using explicit flags
python ciam.py config use --region us --env qa

# Using shorthand
python ciam.py config use us-qa

# With a default store ID
python ciam.py config use --region us --env qa --store-id my-store-id
```

### View Current Configuration

```bash
python ciam.py config get
```

### List Valid Options

```bash
python ciam.py config list
```

## Environment Variables (.env)

The `.env` file stores PingOne credentials. Each region-environment combination requires two sets of credentials:

1. **General credentials**: For all operations except Client operations
   - `{REGION}_{ENV}_GENERAL_CLIENT_ID`
   - `{REGION}_{ENV}_GENERAL_CLIENT_SECRET`

2. **Client operations credentials**: For Client-specific operations
   - `{REGION}_{ENV}_CLIENTOPS_CLIENT_ID`
   - `{REGION}_{ENV}_CLIENTOPS_CLIENT_SECRET`

Example for US-QA:
```
US_QA_GENERAL_CLIENT_ID=your-client-id
US_QA_GENERAL_CLIENT_SECRET=your-client-secret
US_QA_CLIENTOPS_CLIENT_ID=your-client-ops-id
US_QA_CLIENTOPS_CLIENT_SECRET=your-client-ops-secret
```

Regions: `us`, `uk`, `can`, `anz`
Environments: `dev`, `qa`, `uat`, `prod`

## Commands

### Config Management

```bash
# Get current config
python ciam.py config get

# List valid regions/environments
python ciam.py config list

# Set region and environment
python ciam.py config use --region us --env qa

# Set with shorthand
python ciam.py config use us-qa

# Set with default store ID
python ciam.py config use us-qa --store-id store-123
```

### Token Management

```bash
# View current access tokens (unmasked)
python ciam.py tokens view
```

Note: PingOne supports two client-credentials request formats. This CLI uses:
- GENERAL tokens: sent with an `Authorization: Basic <base64(client_id:client_secret)>` header and a form body containing only `grant_type=client_credentials`.
- CLIENT-OPS tokens: sent with `client_id` and `client_secret` in the form body (no Basic header). Use the `{REGION}_{ENV}_CLIENTOPS_*` env vars for client-ops credentials.

### Users

```bash
# Get one or more users by ID
python ciam.py users get user-id-1 [user-id-2 ...]

# With store ID override
python ciam.py users get user-id-1 --store-id different-store

# Import users from JSON file(s)
python ciam.py users import users.json [additional-files.json ...]
```

**Import File Format** (`users.json`):
```json
{
  "type": "users",
  "users": [
    {
      "id": "user-123",
      "email": "user@example.com",
      "name": "John Doe"
    }
  ]
}
```

### Groups

```bash
# Get groups by ID
python ciam.py groups get group-id-1 [group-id-2 ...]

# With store ID override
python ciam.py groups get group-id-1 --store-id different-store
```

### Organizations

```bash
# Get organizations by ID
python ciam.py orgs get org-id-1 [org-id-2 ...]

# With store ID override
python ciam.py orgs get org-id-1 --store-id different-store

# Apply/diff operations (planned for future)
python ciam.py orgs apply org-id-1
python ciam.py orgs diff org-id-1
```

### Stores

```bash
# Get stores by ID (note: store operations don't require store header)
python ciam.py stores get store-id-1 [store-id-2 ...]

# Apply/diff operations (planned for future)
python ciam.py stores apply store-id-1
python ciam.py stores diff store-id-1
```

### Products

```bash
# Get products by ID
python ciam.py products get product-id-1 [product-id-2 ...]

# With store ID override
python ciam.py products get product-id-1 --store-id different-store
```

### Command History

```bash
# Show last 10 commands
python ciam.py history

# Show last N commands (max 100)
python ciam.py history -n 50

# Replay command by index (from history display)
python ciam.py history -r 0  # Replays the most recent command
python ciam.py history -r 5
```

History is stored in `~/.ciam-cli-history.jsonl`.

## Global Flags

All commands support:

```bash
# Verbose mode: shows detailed operation steps and metadata
python ciam.py <command> -v
python ciam.py <command> --verbose
```

## Output

### Terminal Output

Commands use a consistent framing style:

```
▼ get users
  • Fetching user: user-123
    • ✓ Retrieved user user-123: john@example.com
  • Retrieved 1 user(s), 0 error(s)
▲ get users (success)

Output written to: output-20260203_143022.json
```

### JSON Log Files

All API requests and responses are logged to timestamped JSON files in the current directory:

```
output-20260203_143022.json
```

Each entry contains:
```json
{
  "timestamp": "2026-02-03T14:30:22.123456Z",
  "operation": "GET /users/{id}",
  "request": {
    "method": "GET",
    "url": "https://ciam-us-qa.example.com/api/v1/users/user-123",
    "headers": {
      "Authorization": "***REDACTED***",
      "X-Store-Id": "store-123"
    }
  },
  "response": {
    "status_code": 200,
    "headers": {...},
    "body": {...}
  }
}
```

Secrets are automatically redacted in output files unless verbose mode is enabled.

## API Endpoints

The CLI maps to RESTful CIAM API endpoints. Currently implemented:

- `GET /users/{id}` - Fetch user by ID
- `GET /groups/{id}` - Fetch group by ID
- `GET /orgs/{id}` - Fetch organization by ID
- `GET /stores/{id}` - Fetch store by ID
- `GET /products/{id}` - Fetch product by ID

TODO: Update endpoint paths in `ciam/http.py` BASE_URLS to match your actual API.

## Architecture

### Project Structure

```
ciam-cli/
  ciam.py                    # Entry point
  requirements.txt           # Python dependencies
  .env.example              # Environment variable template
  README.md                 # This file
  
  ciam/
    __init__.py
    cli.py                  # Argparse setup and command routing
    config.py               # Configuration management (~/.config-ciam-cli)
    auth.py                 # PingOne OAuth2 token handling
    http.py                 # HTTP client wrapper for API calls
    output.py               # JSON logging to output-<timestamp>.json
    history.py              # Command history tracking and replay
    util.py                 # Shared formatting and utility functions
    
    handlers/
      __init__.py
      users.py              # User domain operations
      groups.py             # Group domain operations
      orgs.py               # Organization domain operations
      stores.py             # Store domain operations
      products.py           # Product domain operations
      clients.py            # Client domain operations (placeholder)
```

### Key Components

- **cli.py**: Argparse configuration and command routing
- **config.py**: Persistent config in `~/.config-ciam-cli` (JSON)
- **auth.py**: OAuth2 token retrieval with in-memory caching
- **http.py**: HTTP wrapper handling authentication headers, store IDs, and logging
- **output.py**: Logs all API calls to timestamped JSON files
- **history.py**: Records and replays commands
- **util.py**: Shared formatting and redaction functions
- **handlers/**: Domain-specific operation handlers

### Authentication Flow

1. User runs a command requiring API access
2. CLI checks configured region and environment
3. `auth.py` fetches PingOne token using stored credentials
4. Token is cached in memory (5-min buffer before expiry)
5. `http.py` injects token into Authorization header
6. API call is made with required headers (including `X-Store-Id` where applicable)
7. Response is logged to JSON output file

### Secret Handling

- By default, secrets are redacted in all output and logs
- Use `python ciam.py tokens view` to see unmasked tokens
- Verbose mode shows more detailed step-by-step output but still redacts secrets (except in tokens view)
- In JSON output files, secrets are redacted unless verbose mode was enabled

## Error Handling

The CLI provides clear error messages for:

- Missing configuration (region/environment not set)
- Missing required store IDs
- Authentication failures
- Invalid credentials
- Network errors
- Malformed JSON responses

Example:
```
Error: Store ID is required. Provide --store-id or set default with 'config use'
```

## Development / Extending

### Adding a New Command

1. Create handler function in `ciam/handlers/`.py
2. Add subparser in `cli.py`
3. Add handler routing in `cli.py`
4. Update this README

### Adding a New Domain Object

1. Create `ciam/handlers/newobject.py`
2. Implement: `list_`, `get_`, `create_`, `update_`, `delete_`, and operation-specific functions
3. Add subparser for the object in `cli.py`
4. Add handler routing

### Updating API Endpoints

Edit `ciam/http.py`:
- Update `BASE_URLS` with real CIAM API base URLs
- Update `PINGONE_TOKEN_URLS` with real PingOne token endpoints
- Update endpoint paths in handlers (e.g., `/users/{id}`)

## Type Hints

The codebase uses Python type hints for better IDE support and maintainability. Run mypy to check:

```bash
pip install mypy
mypy ciam/
```

## Testing

Create a test file to validate the CLI without making real API calls:

```bash
# Example: test with mock responses
python -m pytest tests/
```

## Troubleshooting

### "Missing credentials" error
Ensure `.env` is created and populated with valid PingOne credentials for the current region/environment.

### "Store ID is required" error
Set a default store ID:
```bash
python ciam.py config use us-qa --store-id my-store
```

Or pass it explicitly:
```bash
python ciam.py users get user-id --store-id my-store
```

### Token expiration
Tokens are automatically refreshed when they have <5 min remaining. If issues persist, force a refresh by running `tokens view`.

### Network timeouts
Check your internet connection and confirm API endpoints are accessible. Increase timeout in `http.py` if needed.

## License

Internal use only.

## Support

For issues or feature requests, contact the CIAM support team.
