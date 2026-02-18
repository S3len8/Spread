import aiogram
from calculation import calculation
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8209170851:AAGViuYiZsc7O2m_P-yoMYDKOVmfPcoOZJ4'

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Button
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Active Spread", callback_data="show_spread")]
    ]
)


# Start
@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer('Choose activity:', reply_markup=keyboard)


# Button click processing
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):

    if callback.data == "show_spread":

        data = calculation

        text = ""

        for symbol, value in data.items():
            text += (
                f"🚀 {symbol}\n"
                f"Buy on: {value['buy_on']}\n"
                f"Sell on: {value['sell_on']}\n"
                f"Funding buy: {value['funding buy_on']}\n"
                f"Funding sell: {value['funding sell_on']}\n"
                f"Volume buy 24H: {value['volume_buy_24H']}\n"
                f"Volume sell 24H: {value['volume_sell_24H']}\n"
                f"Spread: {value['spread']}\n\n"
            )

        if not text:
            text = "No spreads for this moment"

        await callback.message.answer(text)
        await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


