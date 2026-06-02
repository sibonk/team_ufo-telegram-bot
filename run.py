import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from database import init_db
from utlis.handlers import router

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")