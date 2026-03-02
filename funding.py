import requests
import asyncio
import aiohttp
from symbol import BINANCE_FUNDING, BYBIT_DATA, BITGET, MEXC, KUCOIN_FUNDING, GATE
from volume import get_summary_volume


def get_funding_binance(summary_volume) -> dict:
    result = {}
    data = requests.get(BINANCE_FUNDING).json()
    for item in data:
        binance_symbol = item['symbol']
        if binance_symbol in summary_volume:
            value = summary_volume[binance_symbol]
            if 'binance' in value['buy_on'] or 'binance' in value['sell_on']:
                result[binance_symbol] = {
                    'exchange': 'binance',
                    'funding': float(item['lastFundingRate'])
                }
    return result


def get_funding_bybit(summary_volume):
    result = {}
    data = requests.get(BYBIT_DATA, params={'category': 'linear'}).json()
    for item in data['result']['list']:
        bybit_symbol = item['symbol']
        if bybit_symbol in summary_volume:
            value = summary_volume[bybit_symbol]
            funding_raw = item.get('fundingRate')
            if any(bybit_symbol.endswith(s) for s in ('PERP', 'USDC', 'USD')):
                continue
            if 'bybit' in value['buy_on'] or 'bybit' in value['sell_on']:
                result[bybit_symbol] = {
                    'exchange': 'bybit',
                    'funding': float(funding_raw)
                }
    return result


def get_funding_bitget(summary_volume):
    result = {}
    data = requests.get(BITGET, params={"productType": "USDT-FUTURES"}).json()
    for item in data['data']:
        bitget_symbol = item['symbol']
        if bitget_symbol in summary_volume:
            value = summary_volume[bitget_symbol]
            if any(bitget_symbol.endswith(s) for s in ('PERP', 'USDC', 'USD')):
                continue
            if 'bitget' in value['buy_on'] or 'bitget' in value['sell_on']:
                result[bitget_symbol] = {
                    'exchange': 'bitget',
                    'funding': float(item['fundingRate'])
                }
    return result


def get_funding_mexc(summary_volume):
    result = {}
    data = requests.get(MEXC).json()
    for item in data['data']:
        mexc_symbol = item['symbol'].replace('_', '')
        if mexc_symbol in summary_volume:
            value = summary_volume[mexc_symbol]
            if any(mexc_symbol.endswith(s) for s in ('PERP', 'USDC', 'USD')):
                continue
            if 'mexc' in value['buy_on'] or 'mexc' in value['sell_on']:
                result[mexc_symbol] = {
                    'exchange': 'mexc',
                    'funding': float(item['fundingRate'])
                }
    return result


def get_funding_gate(summary_volume):
    result = {}
    data = requests.get(GATE).json()
    for item in data:
        gate_symbol = item['contract'].replace('_', '')
        if gate_symbol in summary_volume:
            value = summary_volume[gate_symbol]
            if any(gate_symbol.endswith(s) for s in ('PERP', 'USDC', 'USD')):
                continue
            if 'gate' in value['buy_on'] or 'gate' in value['sell_on']:
                result[gate_symbol] = {
                    'exchange': 'gate',
                    'funding': float(item['funding_rate'])
                }
    return result


def normalize_kucoin_symbol(symbol: str) -> str:
    return symbol.replace('-', '').replace('_', '').replace('USDTM', 'USDT').replace('M', '')


async def fetch_funding_kucoin(session, symbol):
    url = KUCOIN_FUNDING.format(symbol=f"{symbol}M")
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status != 200:
                return None
            data = await r.json(content_type=None)  # ignore Content-Type
            if data.get('code') != "200000":
                return None
            return normalize_kucoin_symbol(symbol), {
                'exchange': 'kucoin',
                'funding': float(data['data']['value'])
            }
    except Exception:
        return None


async def get_funding_kucoin(summary_volume):
    symbols = [
        s for s, v in summary_volume.items()
        if 'kucoin' in v['buy_on'] or 'kucoin' in v['sell_on']
    ]
    if not symbols:
        return {}
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[fetch_funding_kucoin(session, s) for s in symbols])
    return dict(r for r in results if r)


# ✅ async — call async get_summary_volume()
async def get_summary_funding() -> dict:
    summary_volume = await get_summary_volume()

    exchanges = {
        'binance': get_funding_binance(summary_volume),
        'bybit':   get_funding_bybit(summary_volume),
        'bitget':  get_funding_bitget(summary_volume),
        'mexc':    get_funding_mexc(summary_volume),
        'kucoin':  await get_funding_kucoin(summary_volume),
        'gate':    get_funding_gate(summary_volume),
    }

    result = {}
    for symbol, value in summary_volume.items():
        buy_exchange = value['buy_on']
        sell_exchange = value['sell_on']
        if buy_exchange not in exchanges or sell_exchange not in exchanges:
            continue
        result[symbol] = {
            'buy_on': buy_exchange,
            'sell_on': sell_exchange,
            'funding buy_on': exchanges[buy_exchange].get(symbol, {}).get('funding'),
            'funding sell_on': exchanges[sell_exchange].get(symbol, {}).get('funding'),
            'volume_buy_24H': value['volume_buy_24H'],
            'volume_sell_24H': value['volume_sell_24H'],
            'spread': value['spread'],
        }
    return result