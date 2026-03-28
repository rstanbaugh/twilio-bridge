
# Twilio Bridge for OpenClaw

A thin, secure HTTP bridge for relaying Twilio SMS webhooks to a local OpenClaw Gateway, with all configuration via environment variables.

**Voice calling is not handled by this bridge and is instead delegated to the native OpenClaw `voice-call` plugin.**
**No /voice endpoint is present in this bridge for MVP.**

## Overview
- Receives inbound Twilio SMS webhooks (via Cloudflare Tunnel)
- Validates Twilio signatures
- Normalizes and forwards SMS to OpenClaw Gateway using OpenAI-compatible HTTP API
- Returns TwiML responses to Twilio
- SMS fallback message is configurable via environment variable, with a safe default if unset
- Structured logging, health endpoints, and launchd compatibility

## Quick Start

1. **Clone this repo and enter the directory:**
    ```bash
    cd ~/.openclaw/tools/twilio
    ```

2. **Copy and edit the environment file:**
    ```bash
    cp .env.example .env
    # Edit .env with your Twilio and OpenClaw credentials
    ```

3. **Install dependencies (in your project conda environment):**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the bridge:**
    ```bash
    python -m twilio_bridge.main
    ```
    Or use your ~/bin bash wrapper if preferred.

5. **Configure Cloudflare Tunnel** to forward public webhook URLs to your local bridge (see REQUIREMENTS.md for details).

## Environment Variables
All sensitive configuration is set in `.env` (never commit this file):
- TWILIO_AUTH_TOKEN
- OPENCLAW_BASE_URL
- OPENCLAW_GATEWAY_TOKEN
- TWILIO_ACCOUNT_SID
- TWILIO_PHONE_NUMBER
- TWILIO_BRIDGE_HOST
- TWILIO_BRIDGE_PORT
- TWILIO_BRIDGE_LOG_LEVEL
- TWILIO_SMS_FALLBACK_MESSAGE
- TWILIO_VALIDATE_SIGNATURE
- OPENCLAW_TIMEOUT_SECONDS

See `.env.example` for a template.

## Endpoints
- `POST /sms` — Twilio SMS webhook
- `GET /healthz` — Health check
- `GET /readyz` — Readiness check

**No /voice endpoint is present in this bridge. Voice is handled by the OpenClaw plugin.**

## Security
- All secrets and credentials must be set in `.env`
- Never commit `.env` or real credentials to version control
- Twilio signature validation is enforced by default
- Bridge binds to localhost by default; public ingress is via Cloudflare Tunnel only

## Development & Testing
- All configuration is via environment variables
- Tests are in `tests/` and should be run with `pytest`
- No /voice tests are present in this project.
- Use `.env.example` as a safe template for sharing

## See Also
- [REQUIREMENTS.md](REQUIREMENTS.md) — Full requirements and design
- [.env.example](.env.example) — Environment variable template
- [AGENTS.md](AGENTS.md) — Project agent/testing policy

## Cloudflare Tunnel Example
See REQUIREMENTS.md for example Cloudflare Tunnel config snippets. Production tunnel config is deployment-specific and not included in the repo.

---

For questions or contributions, open an issue or contact the maintainers.
# twilio-bridge
