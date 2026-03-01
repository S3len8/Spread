import requests
from symbol import BINANCE_ORDER_BOOK, BINANCE_DATA, BYBIT_DATA, BITGET, MEXC, KUCOIN, GATE
from spread import get_summary


def get_data_binance(summary) -> dict:
    result = {}
    k = requests.get(BINANCE_DATA).json()
    q = requests.get(BINANCE_ORDER_BOOK).json()
    volume = {vol['symbol']: float(vol['quoteVolume']) for vol in k}
    order_book_symbols = {t['symbol'] for t in q}
    for symbol, value in summary.items():
        if 'binance' in value['buy_on'] or 'binance' in value['sell_on']:
            if symbol in order_book_symbols:
                result[symbol] = {'volume 24H': volume.get(symbol, 0.0)}
    return result


def get_data_bybit(summary) -> dict:
    result = {}
    k = requests.get(BYBIT_DATA, params={'category': 'linear'}).json()
    bybit_map = {t['symbol']: t for t in k['result']['list']}
    for symbol, value in summary.items():
        if 'bybit' in value['buy_on'] or 'bybit' in value['sell_on']:
            if symbol in bybit_map:
                result[symbol] = {'volume 24H': float(bybit_map[symbol]['turnover24h'])}
    return result


def get_data_bitget(summary) -> dict:
    result = {}
    k = requests.get(BITGET, params={"productType": "USDT-FUTURES"}).json()
    bitget_map = {t['symbol']: t for t in k['data']}
    for symbol, value in summary.items():
        if 'bitget' in value['buy_on'] or 'bitget' in value['sell_on']:
            if symbol in bitget_map:
                result[symbol] = {'volume 24H': float(bitget_map[symbol]['usdtVolume'])}
    return result


def get_data_mexc(summary) -> dict:
    result = {}
    k = requests.get(MEXC).json()
    mexc_map = {t['symbol'].replace('_', ''): t for t in k['data']}
    for symbol, value in summary.items():
        if 'mexc' in value['buy_on'] or 'mexc' in value['sell_on']:
            if symbol in mexc_map:
                result[symbol] = {'volume 24H': float(mexc_map[symbol]['volume24'])}
    return result


def get_data_kucoin(summary) -> dict:
    result = {}
    all_data = requests.get(KUCOIN).json()
    kucoin_map = {item['symbol']: item for item in all_data['data']}
    for symbol, value in summary.items():
        if 'kucoin' in value['buy_on'] or 'kucoin' in value['sell_on']:
            symbol_kucoin = symbol.replace('USDT', 'USDTM').replace('BTC', 'XBT')
            item = kucoin_map.get(symbol_kucoin, {})
            result[symbol] = {'volume 24H': float(item.get('turnoverOf24h', 0))}
    return result


def get_data_gate(summary) -> dict:
    result = {}
    k = requests.get(GATE).json()
    gate_map = {t['contract'].replace('_', ''): t for t in k}
    for symbol, value in summary.items():
        if 'gate' in value['buy_on'] or 'gate' in value['sell_on']:
            if symbol in gate_map:
                result[symbol] = {'volume 24H': float(gate_map[symbol]['volume_24h_base'])}
    return result


# ✅ async — call async get_summary()
async def get_summary_volume() -> dict:
    summary = await get_summary()

    exchanges = {
        'binance': get_data_binance(summary),
        'bybit':   get_data_bybit(summary),
        'bitget':  get_data_bitget(summary),
        'mexc':    get_data_mexc(summary),
        'kucoin':  get_data_kucoin(summary),
        'gate':    get_data_gate(summary),
    }

    result = {}
    for symbol, value in summary.items():
        buy_exchange = value['buy_on']
        sell_exchange = value['sell_on']
        if symbol in exchanges.get(buy_exchange, {}):
            result[symbol] = {
                'buy_on': buy_exchange,
                'sell_on': sell_exchange,
                'spread': value['spread'],
                'volume_buy_24H': exchanges[buy_exchange].get(symbol, {}).get('volume 24H'),
                'volume_sell_24H': exchanges[sell_exchange].get(symbol, {}).get('volume 24H'),
            }
    return result
