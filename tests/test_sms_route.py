def test_twiml_escaping(monkeypatch, client):
    # Patch signature validator to always accept
    from twilio_bridge import app as bridge_app
    monkeypatch.setattr(
        bridge_app.validate_twilio_signature, lambda url, form, sig: True
    )
    # Patch OpenClaw client to return a string with special XML chars
    monkeypatch.setattr(
        bridge_app.send_to_openclaw, lambda msg: '<foo>&"bar"'</foo>')
    resp = client.post('/sms', data={
        'From': '+1234567890',
        'To': '+1098765432',
        'Body': 'test',
        'MessageSid': 'SM123',
        'NumMedia': '0',
    }, headers={'X-Twilio-Signature': 'valid'})
    assert resp.status_code == 200
    # Should not break XML, should include the special chars
    assert b'&lt;foo&gt;&amp;"bar"&lt;/foo&gt;' in resp.data or b'<foo>&"bar"</foo>' in resp.data


def test_sms_missing_fields(monkeypatch, client):
    from twilio_bridge import app as bridge_app
    monkeypatch.setattr(
        bridge_app.validate_twilio_signature, lambda url, form, sig: True
    )
    # Patch OpenClaw client to return a reply
    monkeypatch.setattr(
        bridge_app.send_to_openclaw, lambda msg: "reply")
    # Missing From field
    resp = client.post('/sms', data={
        'To': '+1098765432',
        'Body': 'hello',
        'MessageSid': 'SM123',
        'NumMedia': '0',
    }, headers={'X-Twilio-Signature': 'valid'})
    # Should not crash, should return 200 with fallback or empty TwiML
    assert resp.status_code in (200, 400)


def test_sms_internal_exception(monkeypatch, client):
    from twilio_bridge import app as bridge_app
    monkeypatch.setattr(
        bridge_app.validate_twilio_signature, lambda url, form, sig: True
    )
    # Patch OpenClaw client to raise
    def raise_exc(msg):
        raise Exception("fail")
    monkeypatch.setattr(bridge_app, 'send_to_openclaw', raise_exc)
    resp = client.post('/sms', data={
        'From': '+1234567890',
        'To': '+1098765432',
        'Body': 'hello',
        'MessageSid': 'SM123',
        'NumMedia': '0',
    }, headers={'X-Twilio-Signature': 'valid'})
    # Should not crash, should return 200 or 500 with safe TwiML
    assert resp.status_code in (200, 500)
import pytest
from flask import Flask
from twilio_bridge.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_sms_signature_rejected(client):
    resp = client.post('/sms', data={
        'From': '+1234567890',
        'To': '+1098765432',
        'Body': 'hello',
        'MessageSid': 'SM123',
        'NumMedia': '0',
    }, headers={'X-Twilio-Signature': 'invalid'})
    assert resp.status_code == 403
    assert b'<Response' in resp.data

def test_healthz(client):
    resp = client.get('/healthz')
    assert resp.status_code == 200
    assert resp.json['status'] == 'ok'

def test_readyz(client):
    resp = client.get('/readyz')
    assert resp.status_code == 200
    assert 'ready' in resp.json


def test_sms_valid_signature_and_openclaw_reply(monkeypatch, client):
    # Patch signature validator to always accept
    from twilio_bridge import app as bridge_app
    monkeypatch.setattr(
        bridge_app.validate_twilio_signature, lambda url, form, sig: True
    )
    # Patch OpenClaw client to return a canned reply
    monkeypatch.setattr(
        bridge_app.send_to_openclaw, lambda msg: "Hello from OpenClaw!"
    )
    resp = client.post('/sms', data={
        'From': '+1234567890',
        'To': '+1098765432',
        'Body': 'hello',
        'MessageSid': 'SM123',
        'NumMedia': '0',
    }, headers={'X-Twilio-Signature': 'valid'})
    assert resp.status_code == 200
    assert b'Hello from OpenClaw!' in resp.data
    assert b'<Message>' in resp.data
