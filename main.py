from contextlib import asynccontextmanager
from calculation import calculation

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Update, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from fastapi import FastAPI, Request

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

SCAN_INTERVAL = 30  # seconds between scans

# ====== Initialization ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ====== State: one monitoring task per chat ======
# chat_id -> asyncio.Task
monitoring_tasks: dict[int, asyncio.Task] = {}

# ====== Keyboard ======
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Active Spreads")],
        [KeyboardButton(text="🛑 Stop Monitoring")],
    ],
    resize_keyboard=True
)


# == Exchange URL ======
def exchange_url(exchange: str, symbol: str) -> str | None:
    base = symbol.replace('USDT', '')
    exchanges = {
        'binance': f"https://www.binance.com/en/futures/{base}USDT",
        'bybit': f"https://www.bybit.com/trade/usdt/{base}USDT",
        'bitget': f"https://www.bitget.com/futures/usdt/{base}USDT",
        'mexc': f"https://futures.mexc.com/exchange/{base}_USDT",
        'gate': f"https://www.gate.io/futures/USDT/{base}_USDT",
        'kucoin': f"https://www.kucoin.com/futures/trade/{base}USDTM",
    }
    return exchanges.get(exchange.lower())


# == Button in Message =====
def create_inline_button(symbol: str, buy_on: str, sell_on: str) -> InlineKeyboardMarkup:
    buttons = []
    buy_url = exchange_url(buy_on, symbol)
    sell_url = exchange_url(sell_on, symbol)
    if buy_on:
        buttons.append(InlineKeyboardButton(text=f"📥 Buy — {buy_on.capitalize()}", url=buy_url))
    if sell_on:
        buttons.append(InlineKeyboardButton(text=f"📤 Sell — {sell_on.capitalize()}", url=sell_url))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


# ====== Monitoring loop ======
async def monitoring_loop(chat_id: int):
    """
    Runs until cancelled.
    Every SCAN_INTERVAL seconds:
      - calls calculation()
      - sends each symbol as a separate message
    """
    await bot.send_message(chat_id, "✅ Monitoring started. Scanning every 30 seconds...")

    while True:
        try:
            data = await calculation()
        except asyncio.CancelledError:  # for stop long-lived processes
            raise
        except Exception as e:
            await bot.send_message(chat_id, f"❌ Error fetching data: {e}")
            await asyncio.sleep(SCAN_INTERVAL)
            continue

        if not data:  # For if coins with spreads not found
            await bot.send_message(chat_id, "🔍 No spreads found on this scan.")
        else:
            for symbol, value in data.items():
                spread_pct = (value['spread'] - 1) * 100
                spread_all_pct = value['spread_all'] if value.get('spread_all') is not None else spread_pct

                funding_buy = value['funding buy_on']
                funding_sell = value['funding sell_on']

                buy_on = value['buy_on']
                sell_on = value['sell_on']

                text = (
                    f"🚀 <b>{symbol}</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"📥 Buy on:  <b>{buy_on.upper()}</b>\n"
                    f"📤 Sell on: <b>{sell_on.upper()}</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"📈 Spread:      <b>{spread_pct:.3f}%</b>\n"
                    f"📊 Spread+Fund: <b>{spread_all_pct:.3f}%</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"💰 Funding buy:  {funding_buy * 100:.4f}%" if funding_buy is not None else f"💰 Funding buy:  —"
                )
                # append rest of message
                text += (
                    f"\n💰 Funding sell: {funding_sell * 100:.4f}%" if funding_sell is not None else f"\n💰 Funding sell: —"
                )
                text += (
                    f"\n━━━━━━━━━━━━━━━━\n"
                    f"📦 Vol buy 24H:  ${value['volume_buy_24H']:,.0f}\n"
                    f"📦 Vol sell 24H: ${value['volume_sell_24H']:,.0f}"
                )

                inline_kb = create_inline_button(symbol, buy_on, sell_on)

                try:
                    await bot.send_message(chat_id, text, reply_markup=inline_kb, parse_mode="HTML")
                except Exception as e:
                    await bot.send_message(chat_id, f"⚠️ Failed to send {symbol}: {e}")

        await asyncio.sleep(SCAN_INTERVAL)


# ====== Handlers ======
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Welcome! Press <b>📊 Active Spreads</b> to start monitoring.\n"
        "Press <b>🛑 Stop Monitoring</b> to stop.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@dp.message(lambda m: m.text == "📊 Active Spreads")
async def spread_handler(message: types.Message):
    chat_id = message.chat.id

    # Cancel existing task for this chat if running
    existing = monitoring_tasks.get(chat_id)
    if existing and not existing.done():
        existing.cancel()
        await message.answer("🔄 Restarting monitoring...")

    # Start new monitoring task
    task = asyncio.create_task(monitoring_loop(chat_id))
    monitoring_tasks[chat_id] = task

    # Clean up task reference when done
    def on_task_done(t: asyncio.Task):
        if monitoring_tasks.get(chat_id) is t:
            monitoring_tasks.pop(chat_id, None)

    task.add_done_callback(on_task_done)


@dp.message(lambda m: m.text == "🛑 Stop Monitoring")
async def stop_handler(message: types.Message):
    chat_id = message.chat.id
    task = monitoring_tasks.get(chat_id)
    if task and not task.done():
        task.cancel()
        await message.answer("🛑 Monitoring stopped.")
    else:
        await message.answer("ℹ️ Monitoring is not running.")


# ====== Lifespan ======
@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print(f"Webhook set: {WEBHOOK_URL}/webhook")
    yield
    # Cancel all running tasks on shutdown
    for task in monitoring_tasks.values():
        task.cancel()
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