import asyncio
from aiogram import Bot, Dispatcher

from utlis.config import settings
from db.models import db

from handlers.app import router as app_route
from handlers.user.user_handler import router as user_route
from handlers.user.user_handler_tickets import router as tickets_route
from handlers.admin.admin_handler import router as admin_route

dp = Dispatcher()

async def main():
    db.create_tables()
    bot = Bot(token=settings.BOT_TOKEN)

    dp.include_router(app_route)
    dp.include_router(user_route)
    dp.include_router(tickets_route)
    dp.include_router(admin_route)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")