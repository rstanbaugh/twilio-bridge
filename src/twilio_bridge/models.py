from typing import Dict, Any

def normalize_sms_request(form: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'channel': 'twilio_sms',
        'user_id': form.get('From'),
        'text': form.get('Body', ''),
        'metadata': {
            'from': form.get('From'),
            'to': form.get('To'),
            'message_sid': form.get('MessageSid'),
            'num_media': int(form.get('NumMedia', 0)),
            'provider': 'twilio',
        }
    }
