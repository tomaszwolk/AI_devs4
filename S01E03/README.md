## How to use

### start server

uv run uvicorn main:app --port 3000

### Get HTTPS by tunneling through pinggy

https://pinggy.io/
ssh -p 443 -R0:127.0.0.1:8080 qr@free.pinggy.io

### Send to verify

curl -X POST https:///verify \
 -H "Content-Type: application/json" \
 -d '{
"apikey": "...",
"task": "proxy",
"answer": {
"url": "https://YOUR-URL.a.free.pinggy.link/proxy",
"sessionID": "twolk_sesja_testowa"
}
}'
