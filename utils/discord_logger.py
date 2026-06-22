import aiohttp
from config import (
    DISCORD_TOKEN,
    LOG_CHANNEL_TICKETS,
    LOG_CHANNEL_JOIN_LEFT,
    LOG_CHANNEL_MESSAGE,
    LOG_CHANNEL_COMMANDS,
    LOG_CHANNEL_MOD_CMD
)

async def send_discord_log(channel_id: str, title: str, description: str, color: int = 0x2b2d31):
    if not DISCORD_TOKEN or not channel_id:
        return
        
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    embed = {
        "title": title,
        "description": description,
        "color": color
    }
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in (200, 204):
                    print(f"Failed to send Discord log: {response.status} - {await response.text()}")
    except Exception as e:
        print(f"Error sending Discord log: {e}")

async def log_ticket(title: str, description: str):
    await send_discord_log(LOG_CHANNEL_TICKETS, title, description, color=0x5865F2)

async def log_join_left(title: str, description: str):
    await send_discord_log(LOG_CHANNEL_JOIN_LEFT, title, description, color=0x3BA55C)

async def log_message(title: str, description: str):
    await send_discord_log(LOG_CHANNEL_MESSAGE, title, description, color=0xFEE75C)

async def log_command(title: str, description: str):
    await send_discord_log(LOG_CHANNEL_COMMANDS, title, description, color=0xEB459E)

async def log_mod_cmd(title: str, description: str):
    await send_discord_log(LOG_CHANNEL_MOD_CMD, title, description, color=0xED4245)
