# Twilio Bridge for OpenClaw — Requirements

## 1. Purpose
- Build a small Twilio ingress adapter for OpenClaw that allows:
    - inbound SMS to reach OpenClaw
    - OpenClaw to generate a reply
    - reply to be returned to Twilio as SMS
    - inbound voice calls to reach a minimal voice endpoint
    - future extension to richer voice interaction
- This service is a **thin HTTP bridge**, not a standalone agent runtime.
- It must fit the existing Odin/OpenClaw architecture:
    - OpenClaw gateway remains bound to `127.0.0.1:18789`
    - Twilio bridge runs locally on Odin
    - public ingress is provided through Cloudflare Tunnel
    - no direct WAN exposure of OpenClaw
- Reference architecture: OpenClaw gateway is loopback-only and accessed through controlled ingress paths.  [oai_citation:0‡odin_configuration.md](sediment://file_00000000ead871f5a12e66c8192fa437)

## 2. Scope

### In Scope (MVP)
- Python service running locally on Odin
- HTTP endpoints for Twilio SMS and Voice webhooks
- Twilio request signature validation
- normalization of inbound Twilio requests into an internal message shape
- forwarding SMS content to local OpenClaw
- returning a TwiML SMS response to Twilio
- minimal voice webhook that returns valid TwiML
- structured logging
- simple configuration via environment variables
- suitable for running under launchd

### Out of Scope (MVP)

- real-time bidirectional voice streaming
- speech-to-text / text-to-speech pipeline
- multi-tenant routing
- admin UI
- database persistence
- direct exposure of OpenClaw to the public internet
- replacing Cloudflare Tunnel
- large-scale outbound campaign messaging
- A2P campaign automation

## 3. External Constraints

### Twilio

- Twilio inbound SMS and Voice use webhooks to send HTTP requests to the application.  [oai_citation:1‡Twilio](https://www.twilio.com/docs/usage/webhooks?utm_source=chatgpt.com)
- Inbound SMS webhooks require a valid TwiML response, even if the response is an empty `<Response/>`.  [oai_citation:2‡Twilio](https://www.twilio.com/docs/usage/webhooks/webhooks-overview?utm_source=chatgpt.com)
- Twilio signs inbound webhook requests using `X-Twilio-Signature`, and the application must validate the signature using the exact request URL, the request parameters, and the Twilio Auth Token.  [oai_citation:3‡Twilio](https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests?utm_source=chatgpt.com)

### Cloudflare Tunnel

- Cloudflare Tunnel provides outbound-only connectivity from the origin to Cloudflare and avoids the need for a publicly routable IP.  [oai_citation:4‡Cloudflare Docs](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/?utm_source=chatgpt.com)
- A locally managed tunnel may route multiple hostnames to local services using a configuration file.  [oai_citation:5‡Cloudflare Docs](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/?utm_source=chatgpt.com)

### OpenClaw / Odin

- OpenClaw gateway must remain loopback-only on Odin and should not be directly exposed to LAN/WAN.  [oai_citation:6‡odin_configuration.md](sediment://file_00000000ead871f5a12e66c8192fa437)

---

## 4. High-Level Architecture
```text
Twilio
  -> HTTPS webhook
  -> Cloudflare
  -> Cloudflare Tunnel
  -> twilio-bridge on Odin
  -> OpenClaw gateway on 127.0.0.1:18789
  -> response back through twilio-bridge
  -> Twilio
```

## 5. Repository / File Placement
Target location: `~/.openclaw/tools/twilio`
Launch point: `~/.openclaw/tools/twilio/twilio-bridge.py`
Environment variables: loaded from `.env` in the project directory (i.e., `~/.openclaw/tools/twilio/.env`) by default. You may override or supplement with a global `.env` if needed for production or multi-tool setups.
Expected initial files:
    ```bash
    twilio/
    README.md
    REQUIREMENTS.md
    twilio-bridge.py
    .env.example
    src/
        twilio_bridge/
        __init__.py
        config.py
        app.py
        routes_sms.py
        routes_voice.py
        twilio_security.py
        openclaw_client.py
        twiml.py
        models.py
        logging_utils.py
    tests/
        test_security.py
        test_sms_route.py
        test_voice_route.py
        test_openclaw_client.py
    ```

## 6. Functional Requirements

### FR-1: Local HTTP Service
The system shall run as a long-lived local HTTP service on Odin.

Requirements:
- bind by default to 127.0.0.1
- default port: 3001
- support override by environment variable
- suitable for launchd execution
- no dependency on interactive shell startup

### FR-2: SMS Webhook Endpoint
- The system shall expose an SMS webhook endpoint:
    `POST /sms`
- Behavior:
    - accept Twilio inbound messaging webhook requests
    - parse form-encoded fields sent by Twilio
    - validate Twilio signature before processing
    - extract at minimum:
        - From
        - To
        - Body
        - MessageSid
        - NumMedia
    - normalize the request into an internal message object
    - forward the normalized message to OpenClaw
    - return a valid TwiML SMS response to Twilio
- Notes:
    - Twilio documents that inbound message webhooks contain sender message details and are delivered to the configured webhook URL. 

### FR-3: Voice Webhook Endpoint
- The system shall expose a Voice webhook endpoint: `POST /voice`
- Behavior for MVP:
	- accept Twilio inbound voice webhook requests
	- validate Twilio signature
	- return valid TwiML for a simple voice response
- Initial MVP response may be one of:
	- a fixed <Say> response
	- a minimal greeting plus hangup
	 -a minimal greeting plus <Gather> stub, if desired
- Notes:
	- Twilio voice calls to a phone number generate an incoming call webhook, and the application responds using TwiML.

### FR-4: Twilio Signature Validation
- The system shall reject unsigned or invalidly signed Twilio requests.
- Requirements:
	- use Twilio Python SDK RequestValidator
	- use the Twilio Auth Token from environment
	- validate with:
	    - exact request URL
	    - form parameters
	    - X-Twilio-Signature
    - return HTTP 403 on validation failure
    - log validation failures without exposing secrets
- **MANDATORY** Twilio explicitly signs inbound requests and provides SDK-based validation guidance

### FR-5: OpenClaw Forwarding
- The system shall forward valid inbound SMS messages to local OpenClaw.
- Requirements:
        - Use OpenAI-compatible OpenResponses HTTP API:
                - POST to `http://127.0.0.1:18789/v1/responses`
                - Headers:
                        - `Authorization: Bearer <gateway_token>`
                        - `Content-Type: application/json`
                        - `x-openclaw-message-channel: twilio-sms`
                - Request body example:
                    {
                        "model": "openclaw/default",
                        "user": "<sender_phone_number>",
                        "input": [
                            {
                                "type": "message",
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_text",
                                        "text": "<SMS body>"
                                    }
                                ]
                            }
                        ]
                    }
                - Parse the `output` field from the JSON response for the reply text.
                - Handle timeouts and non-200 responses gracefully; return a safe fallback SMS if OpenClaw is unavailable.
                - This is the OpenAI-compatible, stable, and recommended approach for automation.

### FR-6: SMS Reply Behavior
- The system shall convert OpenClaw output into a Twilio-compatible SMS response.
- Requirements:
    - return TwiML message content in webhook response for synchronous replies
	- sanitize/trim content if needed to remain reasonable for SMS
	- avoid leaking stack traces or internal errors to the sender
	- if no OpenClaw reply is available, return either:
        - empty <Response/>, or
        - a configured fallback message


### FR-7: Logging
- The system shall provide structured logging.
- Requirements:
	- log startup configuration summary
	- log each inbound request with:
        - route
        - sender
        - destination number
        - Twilio SID if present
        - validation pass/fail
	- redact secrets
	- avoid logging full auth tokens or sensitive headers
	- support plain text logs suitable for launchd/stdout capture

### FR-8: Health / Diagnostics
- The system shall expose lightweight diagnostics.
- Recommended endpoints:
    - `GET /healthz`
    - `GET /readyz`
- Behavior:
	- `/healthz` returns process health
	- `/readyz` optionally verifies config loaded and OpenClaw base URL configured
- These endpoints do not require Twilio signature validation.

## 7. Non-Functional Requirements

### NFR-1: Simplicity
- keep implementation small and readable
- avoid framework complexity beyond what is needed
- prefer straightforward Python over abstraction-heavy architecture

### NFR-2: Reliability
- malformed requests must not crash the service
- OpenClaw errors must not crash the service
- invalid Twilio signatures must fail closed
- startup should fail fast on missing critical configuration

### NFR-3: Security
- bind locally by default
- rely on Cloudflare Tunnel for public ingress
- validate Twilio signatures on Twilio routes
- keep secrets in environment, not source
- do not expose debug mode in production

### NFR-4: Deterministic Configuration
- use environment variables only
- no hidden shell dependencies
- compatible with launchd environment-driven deployment

### NFR-5: Testability
- routes must be testable with local test client
- signature validation must be unit tested
- OpenClaw HTTP client must be mockable
- TwiML generation must be testable independently

## 8. Configuration Requirements

All sensitive configuration values (tokens, URLs, phone numbers, ports, etc.) must be set in the `.env` file in the project directory. Example variable names:
    - TWILIO_AUTH_TOKEN
    - OPENCLAW_BASE_URL
    - OPENCLAW_GATEWAY_TOKEN
    - TWILIO_ACCOUNT_SID
    - TWILIO_PHONE_NUMBER
    - TWILIO_BRIDGE_HOST
    - TWILIO_BRIDGE_PORT
    - TWILIO_BRIDGE_LOG_LEVEL
    - TWILIO_SMS_FALLBACK_MESSAGE
    - TWILIO_VOICE_GREETING
    - TWILIO_VALIDATE_SIGNATURE
    - OPENCLAW_TIMEOUT_SECONDS

See `.env` for actual values. Do not commit secrets or credentials to version control.

Behavior:
    - missing TWILIO_AUTH_TOKEN shall be fatal when signature validation is enabled
    - missing OPENCLAW_BASE_URL may use default localhost value
    - invalid port or malformed URL shall fail startup

## 9. Cloudflare / DNS Assumptions
- The bridge assumes the following hostnames are already routed through Cloudflare Tunnel:
    - `sms.team505.ai`
    - `voice.team505.ai`
- Expected external mapping:
    - `https://sms.team505.ai/sms`
    - `https://voice.team505.ai/voice`
- Cloudflare Tunnel supports mapping hostnames to local HTTP origins via config file ingress rules.  ￼

## 10. Error Handling Requirements
- Invalid Twilio signature
    - return HTTP 403
    - do not process request
    - log warning

- Missing required form fields
    - return HTTP 400 or valid empty TwiML response, depending on route policy
    - log warning

- OpenClaw timeout / connection failure
    - return safe fallback TwiML
    - log error
    - do not expose traceback to user

- Unexpected internal exception
    - return HTTP 500 only if unavoidable
    - prefer valid TwiML fallback where possible
    - log full exception internally

## 11. Suggested Internal Message Shape
- Example normalized inbound SMS object:
    ```JSON
    {
    "channel": "twilio_sms",
    "user_id": "+12485551212",
    "text": "hello odin",
    "metadata": {
        "from": "+12485551212",
        "to": "+12484767665",
        "message_sid": "SMxxxxxxxx",
        "num_media": 0,
        "provider": "twilio"
        }
    }

## 12. Suggested OpenClaw Client Contract
- The bridge should isolate OpenClaw access in one module.
- Suggested behavior:
    - accept normalized input
    - POST to configured OpenClaw endpoint
    - parse a simple reply object
    - return plain text reply to route layer
- Suggested reply shape:
    ```json
    {
    "text": "Hi Rich, Odin here."
    }
    ```
- The exact wire contract may be adapted to current OpenClaw gateway behavior.

## 13. Testing Requirements

Minimum tests:

Unit Tests
	•	valid signature accepted
	•	invalid signature rejected
	•	SMS route parses inbound form fields
	•	voice route returns valid TwiML
	•	TwiML generation escapes content correctly
	•	OpenClaw client handles timeout and non-200 response

Integration Tests
	•	POST /sms with mocked signature validator and mocked OpenClaw response
	•	POST /voice with mocked signature validator
	•	health endpoint responds 200

⸻

## 14. Implementation Preferences
- Python 3.11+
- use argparse only if a small launcher CLI is added
- service entrypoint should be module-based, e.g.:
- python -m twilio-bridge.main
- keep runtime dependencies minimal
- acceptable frameworks:
- Flask
- FastAPI
- Flask is preferred for MVP simplicity unless Codex has a strong reason otherwise

⸻

## 15. Acceptance Criteria
- MVP is complete when all of the following are true:
	1.	Twilio inbound SMS webhook can target: `https://sms.team505.ai/sms`
	2.	Cloudflare Tunnel forwards the request to Odin
	3.	The bridge validates X-Twilio-Signature
	4.	The bridge forwards the message to local OpenClaw
	5.	The bridge returns valid TwiML back to Twilio
	6.	An SMS sent to the Twilio number produces a reply generated by OpenClaw
	7.	Voice webhook at: `https://voice.team505.ai/voice` returns valid TwiML and does not error
	8.	Service runs under launchd without manual shell setup
	9.	Logs are readable and secrets are not exposed

## 16. Future Enhancements
- Not part of MVP, but expected future work:
    - MMS/media handling
    - allowlist of authorized sender numbers
    - per-user identity mapping
    - conversation persistence
    - richer voice flow with <Gather>
    - real-time media streaming / speech pipeline
    - outbound SMS initiated by OpenClaw
    - rate limiting
    - metrics endpoint
    - native OpenClaw channel integration

## 17. Design Principle
- This tool must remain a thin ingress adapter.
- It should:
    - handle Twilio protocol concerns
    - normalize requests
    - delegate intelligence to OpenClaw
    - avoid becoming a second agent runtime
