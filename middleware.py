from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from utils.discord_logger import log_message, log_command, log_mod_cmd
from config import ADMIN_GROUP_ID, PUBLIC_GROUP_ID

class DiscordLogMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Check if it's a message
        if isinstance(event, Message):
            if event.text:
                if event.text.startswith('/'):
                    # It's a command
                    chat_type = event.chat.type
                    is_admin_chat = str(event.chat.id) == str(ADMIN_GROUP_ID)
                    
                    user_info = f"{event.from_user.full_name} (`{event.from_user.id}`)"
                    cmd_info = f"**Command:** {event.text}\n**User:** {user_info}\n**Chat:** {event.chat.title or chat_type}"
                    
                    # Distinguish mod commands vs normal commands
                    mod_cmds = ['/close', '/broadcast', '/invoice']
                    is_mod_cmd = any(event.text.startswith(c) for c in mod_cmds)
                    
                    if is_admin_chat or is_mod_cmd:
                        await log_mod_cmd("Mod Command Executed", cmd_info)
                    else:
                        await log_command("Command Executed", cmd_info)
                elif event.chat.type == 'private':
                    user_info = f"{event.from_user.full_name} (`{event.from_user.id}`)"
                    await log_message(f"Private Message", f"**User:** {user_info}\n**Content:** {event.text}")
                    
        return await handler(event, data)
