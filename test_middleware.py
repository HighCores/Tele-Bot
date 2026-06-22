import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

bot = Bot(token="8407877611:AAEOM7hdrXN45_iKd1QjOT9WWDcMVfKjN58", default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()

class TestMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        print(f"MIDDLEWARE CAUGHT: {event.text}")
        return await handler(event, data)

dp.message.outer_middleware(TestMiddleware())
dp.include_router(router)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
