import aiogram
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = '8209170851:AAGViuYiZsc7O2m_P-yoMYDKOVmfPcoOZJ4'
CHAT_ID = 655882078

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer('Bjk;')


@dp.message
async def get_chat_id(message: types.Message):
    print("CHAT ID:", message.chat.id)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


