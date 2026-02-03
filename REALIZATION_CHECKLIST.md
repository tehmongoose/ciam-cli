# REALIZATION CHECKLIST — Make This CLI Real

This checklist enumerates the concrete, actionable steps required to make the current `ciam-cli` project work end-to-end in production. Each item references the file(s) you will likely edit to complete the task. Do not add new features — only fill in, wire, and verify what's already present.

- [ ] **1) Endpoint & URL Wiring**
  - [ ] Confirm/replace placeholder PingOne token URL(s) in `ciam/auth.py` (update `PINGONE_TOKEN_URLS`).
  - [ ] Confirm/replace placeholder CIAM base URLs mapping in `ciam/http.py` (BASE_URLS or equivalent mapping for each `(region, env)`).
  - [ ] Confirm exact per-domain endpoint paths used by the handlers (e.g., `GET /users/{id}`, import endpoints) and update `ciam/handlers/*.py` and `ciam/http.py` accordingly.
  - [ ] Validate any path/query parameter differences between environments and document them in `README.md` or a config section.

- [ ] **2) Authentication & Token Flows**
  - [ ] Verify GENERAL token flow implementation in `ciam/auth.py` uses `Authorization: Basic <base64(client_id:client_secret)>` and body `grant_type=client_credentials`.
  - [ ] Verify CLIENT-OPS token flow implementation in `ciam/auth.py` posts `client_id`/`client_secret` in the form body and omits the Basic header.
  - [ ] Confirm which PingOne token endpoint is used for GENERAL vs CLIENT-OPS (if different) and set them in `ciam/auth.py`.
  - [ ] Confirm required scopes/audience/resource parameters (if PingOne instance requires `scope` or `audience`) and document where to add them in `ciam/auth.py`.
  - [ ] Ensure token caching/refresh behavior is robust (5-minute buffer) and error cases are logged in `ciam/output.py` via existing logger calls.

- [ ] **3) Environment Secrets / .env Contract**
  - [ ] Define and document exact `.env` keys required (e.g., `{REGION}_{ENV}_GENERAL_CLIENT_ID`, `{REGION}_{ENV}_GENERAL_CLIENT_SECRET`, `{REGION}_{ENV}_CLIENTOPS_CLIENT_ID`, `{REGION}_{ENV}_CLIENTOPS_CLIENT_SECRET`) in `README.md` and `.env.example`.
  - [ ] Add startup validation in `ciam/auth.py` or `ciam/cli.py` to fail fast if required env vars for the configured `region/env` are missing.
  - [ ] Confirm secret redaction rules (where redaction happens) — inspect `ciam/output.py` and `ciam/util.py` and ensure `tokens view` in `ciam/cli.py` intentionally displays unmasked tokens only there.

- [ ] **4) Config File Contract (`.config-ciam-cli`)**
  - [ ] Confirm config file location and schema in `ciam/config.py` (home directory path + JSON keys: region, env, store_id, etc.).
  - [ ] Validate read/write behavior: `config use` writes expected fields and `config get` returns them; test `ciam/cli.py` flows.
  - [ ] Confirm store-id resolution precedence in `ciam/cli.py` and handlers: CLI flag (`--store-id`) > config default > error. Add unit checks or explicit validation where needed.

- [ ] **5) HTTP Request Requirements**
  - [ ] Confirm required headers in `ciam/http.py`: `Authorization: Bearer <token>` and exact store header name (confirm whether `X-Store-Id` is correct) and update code to use the exact header name.
  - [ ] Confirm which operations omit the store header (e.g., store-level operations) and verify handlers match that behavior.
  - [ ] Confirm `Content-Type`/`Accept` requirements and set them globally or per request in `ciam/http.py`.
  - [ ] Confirm TLS/cert expectations and proxy/timeouts: document required CA or client cert settings and ensure `requests` timeouts are set (e.g., 10s) in `ciam/http.py`.
  - [ ] Confirm error handling strategy for non-2xx and non-JSON responses in `ciam/http.py` and ensure those responses are logged to `output-*.json`.

- [ ] **6) Domain Handlers (Supported Today)**
  - For each implemented handler under `ciam/handlers/` (e.g., `users.py`, `groups.py`, `orgs.py`, `stores.py`, `products.py`, `clients.py`):
    - [ ] Confirm the exact endpoint to call and update handler request paths in `ciam/handlers/*.py`.
    - [ ] Confirm required headers/query params for each operation and add explicit validation (fail fast) in each handler.
    - [ ] Confirm response shape (success and error) and decide what is printed to terminal vs written to `output-*.json` (update `handlers` to follow that contract).
    - [ ] For `import` handlers: validate the import file schema in `ciam/handlers/*_import` functions; add clear error messages for malformed files.

- [ ] **7) Output File (`output-<timestamp>.json`)**
  - [ ] Confirm output file naming and location (current directory). Verify `ciam/output.py` writes consistent JSON entries and appends when multiple operations occur.
  - [ ] Confirm all entries redact secrets by default (inspect `ciam/output.py` and `ciam/util.py`) and that verbose mode behavior is documented.
  - [ ] Confirm behavior on failures: ensure a log entry is written for failed requests with request metadata and error summary.

- [ ] **8) History & Replay**
  - [ ] Confirm history file location and format in `ciam/history.py` (`~/.ciam-cli-history.jsonl` or similar) and ensure sensitive arguments are not stored or are redacted.
  - [ ] Confirm maximum history length and rotation (implement or document limit if not present).
  - [ ] Decide and document replay behavior for `history -r`: should replay use the stored argv exactly, or re-resolve config at replay time? Update `ciam/history.py` to match the decision.

- [ ] **9) Packaging & Execution**
  - [ ] Confirm intended invocation: document `python ciam.py ...` and add instructions for installing as a console script (if desired) in `README.md` (do not implement here).
  - [ ] Ensure dependencies in `requirements.txt` are pinned to known-good versions and add notes for supported Python versions (3.11+).
  - [ ] Confirm path handling differences on Windows vs macOS/Linux and test the CLI on each platform (note required adjustments in code if any).

- [ ] **10) Minimal Validation / Smoke Tests (Manual)**
  - Add a short smoke-test plan (manual) to validate the full flow against a safe dev environment. For each command below, run in a dev/qa environment with the `.env` set appropriately and confirm expected behavior; record results.
    - [ ] `python ciam.py config use us-qa --store-id <store>` — verify config writes to `~/.config-ciam-cli` (`ciam/config.py`).
    - [ ] `python ciam.py tokens view` — verify GENERAL and CLIENT-OPS tokens are fetched, cached, and displayed (unmasked) and ensure `output-*.json` contains redacted token request/response entries (`ciam/auth.py`, `ciam/output.py`).
    - [ ] `python ciam.py users get <user-id> --store-id <store>` — verify an authenticated request is sent including the correct store header and that response is printed and logged (`ciam/handlers/users.py`, `ciam/http.py`).

- [ ] **Operational / Documentation**
  - [ ] Update `README.md` with explicit instructions that map to the implemented behavior (exact env var names, required endpoints, sample dev/qa `.env` snippet).
  - [ ] Add a short troubleshooting section for authentication failures and token expiry pointing to `ciam/auth.py` and `ciam/http.py`.

---

Notes / TODO placeholders in code (search for these strings and resolve them):
- `TODO` / `FIXME` occurrences in the repository (start by searching `ciam/` files for these tokens) and resolve any placeholders.

Completion criteria: All checked items should be implemented, tested in a dev/qa environment, and documented in the repository. Once everything above is validated, the current CLI design can be promoted to a production-ready integration (subject to security review and operational checks).
