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
