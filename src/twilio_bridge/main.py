from .app import app
from .config import Config

def main():
    Config.validate()
    app.run(host=Config.TWILIO_BRIDGE_HOST, port=Config.TWILIO_BRIDGE_PORT)

if __name__ == "__main__":
    main()
