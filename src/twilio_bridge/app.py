from flask import Flask, request, Response
from .config import Config
from .logging_utils import setup_logging
from .models import normalize_sms_request
from .twilio_security import validate_twilio_signature
from .openclaw_client import send_to_openclaw
from .twiml import sms_response
import logging

setup_logging(Config.TWILIO_BRIDGE_LOG_LEVEL)
logger = logging.getLogger("twilio_bridge")

app = Flask(__name__)

def get_public_url(request):
    proto = request.headers.get("X-Forwarded-Proto", "http")
    host = request.headers.get("X-Forwarded-Host", request.host)
    return f"{proto}://{host}{request.path}"

@app.route('/sms', methods=['POST'])
def sms_webhook():
    # Validate Twilio signature using the public URL as seen by Twilio
    signature = request.headers.get('X-Twilio-Signature', '')
    public_url = get_public_url(request)
    valid = validate_twilio_signature(public_url, request.form, signature)
    if not valid:
        logger.warning("Invalid Twilio signature", extra={"route": "/sms", "from": request.form.get('From'), "sid": request.form.get('MessageSid')})
        return Response(sms_response(''), status=403, mimetype='application/xml')

    # Normalize and forward
    msg = normalize_sms_request(request.form)
    logger.info("Received SMS", extra=msg['metadata'])
    reply = send_to_openclaw(msg)
    if not reply:
        reply = Config.TWILIO_SMS_FALLBACK_MESSAGE
    return Response(sms_response(reply), mimetype='application/xml')

@app.route('/healthz', methods=['GET'])
def healthz():
    return {"status": "ok"}

@app.route('/readyz', methods=['GET'])
def readyz():
    ready = bool(Config.OPENCLAW_BASE_URL)
    return {"ready": ready}
