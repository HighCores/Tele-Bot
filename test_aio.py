import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
bot = Bot(token="8407877611:AAEOM7hdrXN45_iKd1QjOT9WWDcMVfKjN58")
dp = Dispatcher()
router = Router()
@router.message(F.chat.type == "private")
async def handle(message: Message):
    pass

dp.include_router(router)
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
