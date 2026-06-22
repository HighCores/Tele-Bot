import aiohttp
from datetime import datetime
from config import (
    DISCORD_TOKEN,
    LOG_CHANNEL_TICKETS,
    LOG_CHANNEL_JOIN_LEFT,
    LOG_CHANNEL_MESSAGE,
    LOG_CHANNEL_COMMANDS,
    LOG_CHANNEL_MOD_CMD
)

BANNER_MAIN = "https://i.imgur.com/Lzun3rb.png"

async def send_discord_log(channel_id: str, action: str, user_info: str, details: str, color: int = 0x2b2d31):
    if not DISCORD_TOKEN or not channel_id:
        print(f"DISCORD LOG FAILED: Missing Config. Token={bool(DISCORD_TOKEN)}, Channel={channel_id}")
        return
        
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    print(f"Sending Discord log to {channel_id}: {action}")
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    embed = {
        "author": {"name": "Action Executed"},
        "title": "► Highcore Agency ・ Activity Log",
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {"name": "Action:", "value": f"`{action}`", "inline": False},
            {"name": "User:", "value": user_info, "inline": False}
        ],
        "image": {"url": BANNER_MAIN},
        "footer": {"text": "▪ UNIFIED TERMINAL v1.2.0 • HIGHCORE AGENCY ▪"}
    }

    if details:
        embed["fields"].append({"name": "Details:", "value": details, "inline": False})
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in (200, 204):
                    print(f"Failed to send Discord log: {response.status} - {await response.text()}")
                else:
                    print("Successfully sent Discord log.")
    except Exception as e:
        print(f"Error sending Discord log: {e}")

async def log_ticket(action: str, user_info: str, details: str):
    await send_discord_log(LOG_CHANNEL_TICKETS, action, user_info, details, color=0x5865F2)

async def log_join_left(action: str, user_info: str, details: str):
    await send_discord_log(LOG_CHANNEL_JOIN_LEFT, action, user_info, details, color=0x3BA55C)

async def log_message(action: str, user_info: str, details: str):
    await send_discord_log(LOG_CHANNEL_MESSAGE, action, user_info, details, color=0xFEE75C)

async def log_command(action: str, user_info: str, details: str):
    await send_discord_log(LOG_CHANNEL_COMMANDS, action, user_info, details, color=0xEB459E)

async def log_mod_cmd(action: str, user_info: str, details: str):
    await send_discord_log(LOG_CHANNEL_MOD_CMD, action, user_info, details, color=0xED4245)
