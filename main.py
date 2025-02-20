import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import app.database as sq
from app.handlers import router

load_dotenv()
TOKEN = getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    await sq.db_connect()
    dp.include_router(router)
    print('started')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
