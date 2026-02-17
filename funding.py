import requests
import asyncio
import aiohttp
from symbol import BINANCE_FUNDING, BYBIT_DATA, BITGET, MEXC, KUCOIN_FUNDING, GATE
from volume import summary_volume


# Function get funding from binance, bybit and other exchanges
def get_funding_binance() -> dict:
    result = {}
    # Get funding
    data = requests.get(BINANCE_FUNDING).json()
    for item in data:
        binance_symbol = item['symbol']

        # Check have binance_symbol in summary_volume
        if binance_symbol in summary_volume:
            value = summary_volume[binance_symbol]

            # Check have exchange binance in summary_volume
            if 'binance' in value['buy_on'] or 'binance' in value['sell_on']:
                result[binance_symbol] = {
                    'exchange': 'binance',
                    'funding': float(item['lastFundingRate'])
                }

    return result


def get_funding_bybit():
    result = {}
    # Get data
    data = requests.get(BYBIT_DATA, params={'category': 'linear'}).json()
    for item in data['result']['list']:
        bybit_symbol = item['symbol']

        # Check have bybit_symbol in summary_volume
        if bybit_symbol in summary_volume:
            value = summary_volume[bybit_symbol]

            funding_raw = item.get('fundingRate')  # Need for getting all symbols with and without funding
            if bybit_symbol.endswith('PERP'):
                continue
            if bybit_symbol.endswith('USDC'):
                continue
            if bybit_symbol.endswith('USD'):
                continue

            # Check have exchange bybit in summary_volume
            if 'bybit' in value['buy_on'] or 'bybit' in value['sell_on']:
                result[bybit_symbol] = {
                    'exchange': 'bybit',
                    'funding': float(funding_raw)
                }

    return result


def get_funding_bitget():
    result = {}
    params = {"productType": "USDT-FUTURES"}
    data = requests.get(BITGET, params=params).json()
    for item in data['data']:
        bitget_symbol = item['symbol']

        # Check have bitget_symbol in summary_volume
        if bitget_symbol in summary_volume:
            value = summary_volume[bitget_symbol]

            if bitget_symbol.endswith('PERP'):
                continue
            if bitget_symbol.endswith('USDC'):
                continue
            if bitget_symbol.endswith('USD'):
                continue

            # Check have exchange bitget in summary_volume
            if 'bitget' in value['buy_on'] or 'bitget' in value['sell_on']:
                result[bitget_symbol] = {
                    'exchange': 'bitget',
                    'funding': float(item['fundingRate'])
                }

    return result


def get_funding_mexc():
    result = {}
    data = requests.get(MEXC).json()
    for item in data['data']:
        mexc_symbol = item['symbol'].replace('_', '')

        # Check have mexc_symbol in summary_volume
        if mexc_symbol in summary_volume:
            value = summary_volume[mexc_symbol]

            if mexc_symbol.endswith('PERP'):
                continue
            if mexc_symbol.endswith('USDC'):
                continue
            if mexc_symbol.endswith('USD'):
                continue

            # Check have exchange mexc in summary_volume
            if 'mexc' in value['buy_on'] or 'mexc' in value['sell_on']:
                result[mexc_symbol] = {
                    'exchange': 'mexc',
                    'funding': float(item['fundingRate'])
                }

    return result


def normalize_kucoin_symbol(symbol: str) -> str:
    return (
        symbol
        .replace('-', '')
        .replace('_', '')
        .replace('USDTM', 'USDT')
        .replace('M', '')
    )


def get_kucoin_symbols():
    return [
        symbol
        for symbol, value in summary_volume.items()
        if 'kucoin' in value['buy_on'] or 'kucoin' in value['sell_on']
    ]


async def fetch_funding(session, symbol):
    url = KUCOIN_FUNDING.format(symbol=f"{symbol}M")  # KuCoin требует M

    try:
        async with session.get(url) as r:
            data = await r.json()

            if data.get('code') != "200000":
                return None

            normalized_symbol = normalize_kucoin_symbol(symbol)

            return normalized_symbol, {
                'exchange': 'kucoin',
                'funding': float(data['data']['value'])
            }

    except Exception:
        return None


async def get_funding_kucoin():
    symbols = get_kucoin_symbols()

    if not symbols:
        return {}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_funding(session, s) for s in symbols]
        results = await asyncio.gather(*tasks)

    return dict(r for r in results if r)


def get_funding_gate():
    result = {}
    data = requests.get(GATE).json()
    for item in data:
        gate_symbols = item['contract'].replace('_', '')

        # Check have gate_symbol in summary_volume
        if gate_symbols in summary_volume:
            value = summary_volume[gate_symbols]

            if gate_symbols.endswith('PERP'):
                continue
            if gate_symbols.endswith('USDC'):
                continue
            if gate_symbols.endswith('USD'):
                continue

            # Check have exchange gate in summary_volume
            if 'gate' in value['buy_on'] or 'gate' in value['sell_on']:
                result[gate_symbols] = {
                    'exchange': 'gate',
                    'funding': float(item['funding_rate'])
                }

    return result


get_funding_binance = get_funding_binance()
get_funding_bybit = get_funding_bybit()
get_funding_bitget = get_funding_bitget()
get_funding_mexc = get_funding_mexc()
get_funding_kucoin = asyncio.run(get_funding_kucoin())
get_funding_gate = get_funding_gate()
print(get_funding_binance)
print(get_funding_bybit)
print(get_funding_bitget)
print(get_funding_mexc)
print(get_funding_kucoin)
print(get_funding_gate)


def summary_funding():
    result = {}
    exchanges = {
        'binance': get_funding_binance,
        'bybit': get_funding_bybit,
        'bitget': get_funding_bitget,
        'mexc': get_funding_mexc,
        'kucoin': get_funding_kucoin,
        'gate': get_funding_gate,
    }
    for symbol, value in summary_volume.items():
        buy_exchange = value['buy_on']
        sell_exchange = value['sell_on']

        # Check exchanges in dictionary exchanges
        if buy_exchange not in exchanges or sell_exchange not in exchanges:
            continue

        buy_funding = exchanges[buy_exchange].get(symbol, {}).get('funding')
        sell_funding = exchanges[sell_exchange].get(symbol, {}).get('funding')

        result[symbol] = {
            'buy_on': value['buy_on'],
            'sell_on': value['sell_on'],
            'funding buy_on': buy_funding,
            'funding sell_on': sell_funding,
            'volume_buy_24H': value['volume_buy_24H'],
            'volume_sell_24H': value['volume_sell_24H'],
            'spread': value['spread'],
        }

    return result


summary_funding = summary_funding()
print(summary_funding)


for symbol, data in summary_funding.items():
    print(symbol, data)