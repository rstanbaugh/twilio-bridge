from twilio_bridge.twilio_security import validate_twilio_signature
from twilio_bridge.config import Config
import pytest

def test_signature_validation_disabled(monkeypatch):
    monkeypatch.setattr(Config, 'TWILIO_VALIDATE_SIGNATURE', False)
    assert validate_twilio_signature('url', {}, 'sig') is True

def test_signature_validation_missing_token(monkeypatch):
    monkeypatch.setattr(Config, 'TWILIO_VALIDATE_SIGNATURE', True)
    monkeypatch.setattr(Config, 'TWILIO_AUTH_TOKEN', None)
    assert validate_twilio_signature('url', {}, 'sig') is False
