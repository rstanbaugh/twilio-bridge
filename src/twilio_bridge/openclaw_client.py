import requests
from .config import Config

def send_to_openclaw(normalized_msg):
    url = f"{Config.OPENCLAW_BASE_URL}/v1/responses"
    headers = {
        'Authorization': f'Bearer {Config.OPENCLAW_GATEWAY_TOKEN}',
        'Content-Type': 'application/json',
        'x-openclaw-message-channel': 'twilio-sms',
    }
    data = {
        "model": "openclaw/default",
        "user": normalized_msg['user_id'],
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": normalized_msg['text']
                    }
                ]
            }
        ]
    }
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=Config.OPENCLAW_TIMEOUT_SECONDS)
        if resp.status_code == 200:
            out = resp.json()
            return out.get('output', [{}])[0].get('text') or out.get('text')
        else:
            return None
    except Exception:
        return None
