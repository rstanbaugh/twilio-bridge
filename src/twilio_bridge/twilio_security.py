from twilio.request_validator import RequestValidator
from .config import Config

validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)

def validate_twilio_signature(request_url, form, signature):
    if not Config.TWILIO_VALIDATE_SIGNATURE:
        return True
    if not Config.TWILIO_AUTH_TOKEN:
        return False
    return validator.validate(request_url, form, signature)
