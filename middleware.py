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
        import logging
        logging.info(f"MIDDLEWARE TRIGGERED. Event Type: {type(event)}")
        
        # Check if it's a message
        if isinstance(event, Message):
            logging.info(f"Message received: text={event.text}, chat_type={event.chat.type}")
            if event.text:
                user_info = f"@{event.from_user.username or event.from_user.first_name} (`{event.from_user.id}`)"
                chat_title = event.chat.title or 'Private Chat'
                
                if event.text.startswith('/'):
                    # It's a command
                    is_admin_chat = str(event.chat.id) == str(ADMIN_GROUP_ID)
                    
                    # Distinguish mod commands vs normal commands
                    mod_cmds = ['/close', '/broadcast', '/invoice']
                    is_mod_cmd = any(event.text.startswith(c) for c in mod_cmds)
                    
                    channel_name = "# ⛔mods-cmd・logs" if is_mod_cmd or is_admin_chat else "# ⛔commands・logs"
                    action_name = "Command Executed" if not event.edit_date else "Command Edited"
                    details = f"### 💬 {action_name}\n■ Channel: `{channel_name}`\n■ Content:\n```\n{event.text}\n```"
                    
                    if is_admin_chat or is_mod_cmd:
                        await log_mod_cmd(event.text.split()[0], user_info, details)
                    else:
                        await log_command(event.text.split()[0], user_info, details)
                else:
                    channel_name = "# ⛔message・logs"
                    action_name = "Transmission Intercepted" if not event.edit_date else "Transmission Edited"
                    log_action = "/message-sent" if not event.edit_date else "/message-edited"
                    details = f"### 💬 {action_name}\n■ Channel: `{channel_name}`\n■ Content:\n```\n{event.text}\n```"
                    await log_message(log_action, user_info, details)
                    
        return await handler(event, data)
