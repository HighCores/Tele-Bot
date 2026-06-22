import asyncio 
import logging 
from aiogram import Bot ,Dispatcher 
from config import BOT_TOKEN 
from handlers import panels ,tickets ,orders ,admin ,welcome 
from middleware import DiscordLogMiddleware
from aiogram .client .default import DefaultBotProperties 

async def main ():
    logging .basicConfig (level =logging .INFO ,format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    bot =Bot (token =BOT_TOKEN ,default =DefaultBotProperties (parse_mode ="HTML"))
    dp =Dispatcher ()
    
    dp.message.middleware(DiscordLogMiddleware())

    dp .include_router (admin .router )
    dp .include_router (panels .router )
    dp .include_router (tickets .router )
    dp .include_router (orders .router )
    dp .include_router (welcome .router )

    logging .info ("Starting HighCore Telegram Bot...")
    await bot .delete_webhook (drop_pending_updates =True )
    await dp .start_polling (bot )

if __name__ =="__main__":
    asyncio .run (main ())