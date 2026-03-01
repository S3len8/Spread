from contextlib import asynccontextmanager
from calculation import calculation

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Update
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

from fastapi import FastAPI, Request

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ====== Initialization ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ====== Keyboard ======
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Active Spreads", callback_data="show_spread")]
    ]
)


# ====== Handlers ======
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Choose activity:", reply_markup=keyboard)


@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    if callback.data == "show_spread":
        # Closed callback
        await callback.answer("⏳ Loading...")
        msg = await callback.message.answer("🔄 Fetching data from exchanges...")

        data = await calculation()

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

        # Telegram have limitation for messages in 4096 symbols
        try:
            await msg.edit_text(text[:4096])
        except TelegramBadRequest:
            pass


# ====== Lifespan ======
@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print(f"Webhook set: {WEBHOOK_URL}/webhook")
    yield
    await bot.delete_webhook()
    print("Webhook deleted")


# ====== FastAPI ======
app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def health_check():
    return {"status": "running"}
