from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests
import re
import os
import asyncio
from aiohttp import web

# Configuration from environment variables
API_ID = int(os.getenv('TG_API_ID', '0'))
API_HASH = os.getenv('TG_API_HASH', '')
SESSION_STRING = os.getenv('TG_SESSION_STRING', '')
PHONE = os.getenv('TG_PHONE', '')
CHANNEL = os.getenv('TG_CHANNEL', '')
N8N_WEBHOOK = os.getenv('N8N_WEBHOOK', '')
HEALTH_PORT = int(os.getenv('HEALTH_PORT', '8000'))

# Global health status
health_status = {'status': 'starting', 'last_message': None, 'connected': False}

# Health check endpoint for Coolify
async def health_check(request):
    if health_status['connected']:
        return web.json_response(health_status, status=200)
    else:
        return web.json_response(health_status, status=503)

async def start_health_server():
    """Start health check HTTP server"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', HEALTH_PORT)
    await site.start()
    print(f"✓ Health check server running on port {HEALTH_PORT}")

# Initialize Telegram client
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient('/data/monitor_session', API_ID, API_HASH)
    
@client.on(events.NewMessage(chats=CHANNEL))
async def handler(event):
    """Handle new messages from monitored channel"""
    message = event.message.message
    
    # Update health status
    health_status['last_message'] = event.date.isoformat()
    health_status['status'] = 'running'
    
    # Solana contract address regex (base58, 32-44 characters)
    addresses = re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', message)
    
    if addresses:
        for address in addresses:
            payload = {
                'contractAddress': address,
                'sourceMessage': message,
                'timestamp': event.date.isoformat(),
                'channel': CHANNEL
            }
            
            try:
                response = requests.post(N8N_WEBHOOK, json=payload, timeout=10)
                print(f"✓ Forwarded {address} to n8n (Status: {response.status_code})")
            except requests.exceptions.RequestException as e:
                print(f"✗ Error forwarding to n8n: {e}")
            except Exception as e:
                print(f"✗ Unexpected error: {e}")

async def main():
    """Main entry point"""
    print("=" * 50)
    print("Telegram Solana Monitor")
    print("=" * 50)
    
    # Validate environment variables
    if not all([API_ID, API_HASH, CHANNEL, N8N_WEBHOOK]):
        print("✗ ERROR: Missing required environment variables")
        print("Required: TG_API_ID, TG_API_HASH, TG_CHANNEL, N8N_WEBHOOK")
        print("Optional: TG_SESSION_STRING (recommended) or TG_PHONE (requires interactive auth)")
        health_status['status'] = 'error'
        health_status['connected'] = False
        await start_health_server()
        await asyncio.Event().wait()
        return
    
    # Start health check server
    await start_health_server()
    
    try:
        # Start Telegram client
        if SESSION_STRING:
            print("✓ Using session string authentication")
            await client.connect()
        else:
            print("⚠ Using interactive authentication (requires phone)")
            await client.start(phone=PHONE)
        
        health_status['connected'] = True
        health_status['status'] = 'connected'
        
        print(f"✓ Connected to Telegram")
        print(f"✓ Monitoring channel: @{CHANNEL}")
        print(f"✓ Webhook: {N8N_WEBHOOK}")
        print("✓ Waiting for messages...")
        print("=" * 50)
        
        # Keep running
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        health_status['status'] = 'error'
        health_status['connected'] = False
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
