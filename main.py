import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router

from dotenv import load_dotenv
from os import getenv
import app.database as sq

load_dotenv()
TOKEN = getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await sq.db_connect()
    dp.include_router(router)
    print('start')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
