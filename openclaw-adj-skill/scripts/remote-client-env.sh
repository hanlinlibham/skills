# OpenClaw Remote Client Configuration
# Source this file to configure your local Claude Code to connect to remote OpenClaw

# Replace with your server's IP and token
export OPENCLAW_INSTANCES='{
  "main": {
    "url": "ws://YOUR_SERVER_IP:8789",
    "token": "YOUR_SECURE_TOKEN_HERE",
    "label": "闪电助手"
  }
}'

# Alternative: Using environment variables for single instance
# export OPENCLAW_GATEWAY_URL="ws://YOUR_SERVER_IP:8789"
# export OPENCLAW_GATEWAY_TOKEN="YOUR_SECURE_TOKEN_HERE"

# For SSH tunnel (recommended for security)
# Run: ssh -N -L 8789:localhost:8789 your-user@your-server
# Then:
# export OPENCLAW_GATEWAY_URL="ws://localhost:8789"
# export OPENCLAW_GATEWAY_TOKEN="YOUR_SECURE_TOKEN_HERE"

echo "OpenClaw remote client configuration loaded"
echo "Gateway: $OPENCLAW_GATEWAY_URL"
