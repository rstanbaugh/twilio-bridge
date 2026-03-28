from xml.etree.ElementTree import Element, tostring

def sms_response(message: str) -> str:
    response = Element('Response')
    if message:
        sms = Element('Message')
        sms.text = message
        response.append(sms)
    return tostring(response, encoding='unicode')
