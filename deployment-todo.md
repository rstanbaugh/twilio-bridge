## Cloudflare Tunnel (Headless Startup)

Current setup:
- Tunnel is manually started via:
  cloudflared tunnel run odin-tunnel

This means:
- Tunnel is NOT persistent across reboot
- Requires manual start after restart

### Future Work (Headless / Production)

To support headless startup on Odin:

- Install cloudflared as a system LaunchDaemon:
  sudo cloudflared service install

- Move config from:
  ~/.cloudflared/
  to:
  /etc/cloudflared/

- Update config paths accordingly

- Verify tunnel starts at boot without user login

### Dependency

The tunnel must be running for:
- Twilio SMS webhook (sms.team505.ai)
- External access to the bridge

If the tunnel is down:
- SMS will fail
- Endpoint will be unreachable