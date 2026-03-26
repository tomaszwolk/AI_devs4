## How to use

### Get HTTPS by tunneling through pinggy

https://pinggy.io/
ssh -p 443 -R0:127.0.0.1:8080 qr@free.pinggy.io

copy url to MY_TOOL_URL in config.py with "/api/search" at the end

### start server

uv run uvicorn main:app --port 3000
