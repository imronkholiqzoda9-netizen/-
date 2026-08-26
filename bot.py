import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import client, admin

logging.basicConfig(level=logging.INFO)

async def main():
    # Ташаббуси пойгоҳи додаҳо
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистратсияи роутерҳо
    dp.include_router(admin.router)
    dp.include_router(client.router)
    
    print("🤖 Бот бо муваффақият корро оғоз кард...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())