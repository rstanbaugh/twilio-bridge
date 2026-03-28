from twilio_bridge.openclaw_client import send_to_openclaw
import pytest

def test_openclaw_timeout(monkeypatch):
    def fake_post(*a, **k):
        raise Exception("timeout")
    monkeypatch.setattr("requests.post", fake_post)
    msg = {'user_id': '+1', 'text': 'hi'}
    assert send_to_openclaw(msg) is None
