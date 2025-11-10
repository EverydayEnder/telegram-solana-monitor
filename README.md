# Telegram Solana Monitor

Monitors Telegram channels for Solana contract addresses and forwards them to n8n for automated trading.

## Setup

### 1. Get Telegram API Credentials
1. Go to https://my.telegram.org
2. Login with your phone number
3. Go to "API development tools"
4. Create an app to get `api_id` and `api_hash`

### 2. Configure Environment Variables
Set these in Coolify:
- `TG_API_ID`: Your API ID from my.telegram.org
- `TG_API_HASH`: Your API Hash from my.telegram.org
- `TG_PHONE`: Your phone number with country code (e.g., +1234567890)
- `TG_CHANNEL`: Channel username without @ (e.g., "pumpfun")
- `N8N_WEBHOOK`: Your n8n webhook URL

### 3. First Run Authentication
On first deployment, the container will need to authenticate:
1. Check container logs in Coolify
2. You'll receive a code via Telegram
3. Enter it in the logs (Coolify console)
4. Session is saved and won't ask again

## Health Check
- Endpoint: `http://container:8000/health`
- Returns 200 when connected, 503 when not

## Monitoring Multiple Channels
Set `TG_CHANNEL` to comma-separated list: `channel1,channel2,channel3`
(Requires code modification - see telegram_monitor.py)
```

### 7. **requirements.txt**
```
telethon==1.36.0
requests==2.31.0
aiohttp==3.9.1
