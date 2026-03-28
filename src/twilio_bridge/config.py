import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Always load ~/.openclaw/tools/twilio/.env if present
_env_path = Path(__file__).parent.parent.parent / ".env"
if load_dotenv and _env_path.exists():
    load_dotenv(dotenv_path=_env_path, override=False)

class Config:
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    TWILIO_BRIDGE_HOST = os.getenv('TWILIO_BRIDGE_HOST', '127.0.0.1')
    TWILIO_BRIDGE_PORT = int(os.getenv('TWILIO_BRIDGE_PORT', '3001'))
    TWILIO_BRIDGE_LOG_LEVEL = os.getenv('TWILIO_BRIDGE_LOG_LEVEL', 'INFO')
    TWILIO_SMS_FALLBACK_MESSAGE = os.getenv('TWILIO_SMS_FALLBACK_MESSAGE', 'Odin is temporarily unavailable.')
    TWILIO_VALIDATE_SIGNATURE = os.getenv('TWILIO_VALIDATE_SIGNATURE', 'true').lower() == 'true'
    OPENCLAW_BASE_URL = os.getenv('OPENCLAW_BASE_URL', 'http://127.0.0.1:18789')
    OPENCLAW_GATEWAY_TOKEN = os.getenv('OPENCLAW_GATEWAY_TOKEN')
    OPENCLAW_TIMEOUT_SECONDS = int(os.getenv('OPENCLAW_TIMEOUT_SECONDS', '10'))

    @classmethod
    def validate(cls):
        if cls.TWILIO_VALIDATE_SIGNATURE and not cls.TWILIO_AUTH_TOKEN:
            raise RuntimeError("TWILIO_AUTH_TOKEN is required when signature validation is enabled. Set it in ~/.openclaw/tools/twilio/.env or your environment.")
