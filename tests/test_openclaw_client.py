def test_openclaw_non_200(monkeypatch):
    class FakeResp:
        status_code = 500
        def json(self):
            return {"output": [{"text": "fail"}]}
    def fake_post(*a, **k):
        return FakeResp()
    monkeypatch.setattr("requests.post", fake_post)
    msg = {'user_id': '+1', 'text': 'hi'}
    assert send_to_openclaw(msg) is None
from twilio_bridge.openclaw_client import send_to_openclaw
import pytest

def test_openclaw_timeout(monkeypatch):
    def fake_post(*a, **k):
        raise Exception("timeout")
    monkeypatch.setattr("requests.post", fake_post)
    msg = {'user_id': '+1', 'text': 'hi'}
    assert send_to_openclaw(msg) is None
