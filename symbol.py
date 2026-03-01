import aiohttp
import asyncio
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# ====== URLs ======
BINANCE_ORDER_BOOK = 'https://fapi.binance.com/fapi/v1/ticker/bookTicker'
BINANCE_DATA = 'https://fapi.binance.com/fapi/v1/ticker/24hr'
BINANCE_FUNDING = 'https://fapi.binance.com/fapi/v1/premiumIndex'
BINANCE_FEES = 'https://fapi.binance.com/fapi/v1/commissionRate'
BYBIT_DATA = 'https://api.bybit.com/v5/market/tickers'
BITGET = 'https://api.bitget.com/api/v2/mix/market/tickers'
MEXC = 'https://contract.mexc.com/api/v1/contract/ticker'
KUCOIN = 'https://api-futures.kucoin.com/api/v1/contracts/active'
KUCOIN_FUNDING = "https://api-futures.kucoin.com/api/v1/funding-rate/{symbol}/current"
KUCOIN_ORDER_BOOK = 'https://api-futures.kucoin.com/api/v1/ticker'
GATE = 'https://api.gateio.ws/api/v4/futures/usdt/tickers'

FEES = {
    'Binance': {'maker': 0.02, 'taker': 0.05},
    'Bybit':   {'maker': 0.036, 'taker': 0.1},
    'Bitget':  {'maker': 0.02, 'taker': 0.06},
    'MEXC':    {'maker': 0.01, 'taker': 0.04},
    'Gate':    {'maker': 0.02, 'taker': 0.05},
    'Kucoin':  {'maker': 0.02, 'taker': 0.06},
}


# ====== Helpers ======
def normalize(symbol: str) -> str:
    return (symbol
        .replace('USDTM', '').replace('USDT', '').replace('PERP', '')
        .replace('USDC', '').replace('_USDT', '').replace('XBT', 'BTC')
        .replace('USD', '').replace('_', ''))


async def fetch_json(session, url, params=None):
    async with session.get(url, params=params) as response:
        return await response.json()


# ====== Symbol lists ======
def get_binance_symbols():
    data = requests.get('https://fapi.binance.com/fapi/v1/exchangeInfo').json()
    return [{'symbol': s['symbol']} for s in data['symbols'] if s['contractType'] == 'PERPETUAL']


def get_bybit_symbols():
    data = requests.get('https://api.bybit.com/v5/market/instruments-info',
                        params={'category': 'linear', 'settleCoin': 'USDT'}).json()
    return [{'symbol': s['symbol']} for s in data['result']['list']
            if s['status'] == 'Trading' and s['contractType'] == 'LinearPerpetual']


def get_bitget_symbols():
    data = requests.get(BITGET, params={"productType": "USDT-FUTURES"}).json()
    return [{'symbol': s['symbol']} for s in data['data']]


def get_mexc_symbols():
    data = requests.get(MEXC).json()
    return [{'symbol': k['symbol'].replace('_', '')} for k in data['data']]


def get_gate_symbols():
    data = requests.get(GATE).json()
    return [{'symbol': k['contract'].replace('_', '')} for k in data]


async def get_kucoin_symbols_async(session):
    data = await fetch_json(session, KUCOIN)
    return [{'symbol': item['symbol']} for item in data['data']]


def get_common_symbols(binance, bybit, bitget, mexc, kucoin, gate):
    sets = [
        {normalize(i['symbol']) for i in exchange}
        for exchange in [binance, bybit, bitget, mexc, kucoin, gate]
    ]
    return list(set().union(*sets))


# ====== Bid/Ask ======
def get_spread_binance(common_symbols) -> dict:
    symbols_set = set(common_symbols)
    result = {}
    v = requests.get(BINANCE_ORDER_BOOK).json()
    for key in v:
        symbol = key['symbol']
        if symbol.endswith(('USDC', 'USD')):
            continue
        if symbol in symbols_set:
            continue
        result[symbol] = {
            'bid': float(key['bidPrice']),
            'ask': float(key['askPrice']),
        }
    return result


def get_spread_bitget() -> dict:
    result = {}
    k = requests.get(BITGET, params={"productType": "USDT-FUTURES"}).json()
    for t in k['data']:
        result[t['symbol']] = {
            'bid': float(t['bidPr']),
            'ask': float(t['askPr']),
        }
    return result


def get_spread_mexc(common_symbols) -> dict:
    symbols_set = set(common_symbols)
    result = {}
    k = requests.get(MEXC).json()
    for t in k['data']:
        symbol = t['symbol']
        norm = symbol.replace('_', '')
        if symbol.endswith(('USDC', 'USD')):
            continue
        if norm in symbols_set:
            continue
        result[norm] = {
            'bid': float(t['bid1']) if t.get('bid1') else None,
            'ask': float(t['ask1']) if t.get('ask1') else None,
        }
    return result


def get_spread_gate(common_symbols) -> dict:
    symbols_set = set(common_symbols)
    result = {}
    data = requests.get(GATE).json()
    for key in data:
        symbol = key['contract']
        norm = symbol.replace('_', '')
        if norm in symbols_set:
            continue
        result[norm] = {
            'bid': float(key['highest_bid']),
            'ask': float(key['lowest_ask']),
        }
    return result


async def get_spread_bybit_async(session) -> dict:
    result = {}
    data = await fetch_json(session, BYBIT_DATA, params={'category': 'linear'})
    for t in data['result']['list']:
        symbol = t['symbol']
        if symbol.endswith(('PERP', 'USDC', 'USD')):
            continue
        result[symbol] = {
            'bid': float(t['bid1Price']),
            'ask': float(t['ask1Price']),
        }
    return result


async def get_spread_kucoin_async(session, symbols) -> dict:
    tasks = [fetch_json(session, KUCOIN_ORDER_BOOK, {"symbol": s}) for s in symbols]
    responses = await asyncio.gather(*tasks)
    result = {}
    for symbol, response in zip(symbols, responses):
        data = response.get('data')
        if not data:
            continue
        result[symbol] = {
            'bid': float(data['bestBidPrice']),
            'ask': float(data['bestAskPrice']),
        }
    return result


# ====== Main entry point ======
async def get_source_data():
    import time

    # Symbols
    async with aiohttp.ClientSession() as session:
        t = time.time()
        kucoin_symbols_raw = await get_kucoin_symbols_async(session)
        print(f"kucoin symbols: {time.time()-t:.2f}s")

    t = time.time()
    binance = get_binance_symbols()
    print(f"binance symbols: {time.time()-t:.2f}s")

    t = time.time()
    bybit_sym = get_bybit_symbols()
    print(f"bybit symbols: {time.time()-t:.2f}s")

    t = time.time()
    bitget = get_bitget_symbols()
    print(f"bitget symbols: {time.time()-t:.2f}s")

    t = time.time()
    mexc = get_mexc_symbols()
    print(f"mexc symbols: {time.time()-t:.2f}s")

    t = time.time()
    gate = get_gate_symbols()
    print(f"gate symbols: {time.time()-t:.2f}s")

    common_symbols = get_common_symbols(binance, bybit_sym, bitget, mexc, kucoin_symbols_raw, gate)
    kucoin_symbols = [item['symbol'] for item in kucoin_symbols_raw]

    # Orderbooks (bybit and kucoin — async parallel)
    async with aiohttp.ClientSession() as session:
        t = time.time()
        bybit_data, kucoin_data = await asyncio.gather(
            get_spread_bybit_async(session),
            get_spread_kucoin_async(session, kucoin_symbols),
        )
        print(f"bybit+kucoin spreads: {time.time()-t:.2f}s")

    kucoin_normalized = {
        symbol.replace('XBT', 'BTC').replace('USDTM', 'USDT'): value
        for symbol, value in kucoin_data.items()
    }

    source_data = {
        'bybit': bybit_data,
        'kucoin': kucoin_normalized,
    }

    t = time.time()
    binance_funding = get_spread_binance(common_symbols)
    print(f"binance spreads: {time.time()-t:.2f}s")

    t = time.time()
    bitget_funding = get_spread_bitget()
    print(f"bitget spreads: {time.time()-t:.2f}s")

    t = time.time()
    mexc_funding = get_spread_mexc(common_symbols)
    print(f"mexc spreads: {time.time()-t:.2f}s")

    t = time.time()
    gate_funding = get_spread_gate(common_symbols)
    print(f"gate spreads: {time.time()-t:.2f}s")

    return source_data, binance_funding, bitget_funding, mexc_funding, gate_funding
