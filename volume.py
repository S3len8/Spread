import requests
from symbol import BINANCE_ORDER_BOOK, BINANCE_DATA, BYBIT_DATA, BITGET, MEXC, KUCOIN, KUCOIN_ORDER_BOOK, GATE
from spread import summary


# Function for data binance
def get_data_binance() -> dict:
    result = {}
    # Get volume
    k = requests.get(BINANCE_DATA).json()
    # Get orderbook
    q = requests.get(BINANCE_ORDER_BOOK).json()
    for symbol, value in summary.items():
        if 'binance' in value['buy_on'] or 'binance' in value['sell_on']:
            volume = {vol['symbol']: float(vol['quoteVolume']) for vol in k}
            for t in q:
                if t['symbol'] == symbol:
                    result[symbol] = {
                        'volume 24H': volume.get(symbol, 0.0),
                    }
    return result


def get_data_bybit() -> dict:
    result = {}
    for symbol, value in summary.items():
        if 'bybit' in value['buy_on'] or 'bybit' in value['sell_on']:
            # Get data
            k = requests.get(BYBIT_DATA, params={'category': 'linear'}).json()

            for t in k['result']['list']:
                if t['symbol'] == symbol:
                    result[symbol] = {
                        'volume 24H': float(t['turnover24h']),
                    }
    return result


def get_data_bitget() -> dict:
    result = {}
    for symbol, value in summary.items():
        if 'bitget' in value['buy_on'] or 'bitget' in value['sell_on']:
            params = {"productType": "USDT-FUTURES"}
            k = requests.get(BITGET, params=params).json()
            for t in k['data']:
                if t['symbol'] == symbol:
                    result[symbol] = {
                        'volume 24H': float(t['usdtVolume']),
                    }
    return result


def get_data_mexc() -> dict:
    result = {}
    for symbol, value in summary.items():
        if 'mexc' in value['buy_on'] or 'mexc' in value['sell_on']:
            k = requests.get(MEXC).json()
            for t in k['data']:
                if t['symbol'] == symbol.replace('USDT', '_USDT'):
                    result[symbol] = {
                        'volume 24H': float(t['volume24']),
                    }
    return result


def get_data_kucoin() -> dict:
    result = {}
    for symbol, value in summary.items():
        if 'kucoin' in value['buy_on'] or 'kucoin' in value['sell_on']:
            symbol_kucoin = symbol.replace('USDT', 'USDTM').replace('BTC', 'XBT')
            d = requests.get(KUCOIN, params={"symbol": symbol_kucoin}).json()
            for c in d["data"]:
                if c["symbol"] == symbol_kucoin:
                    volume = float(c.get("turnoverOf24h", 0))
            result[symbol] = {
                'volume 24H': volume,
            }
    return result


def get_data_gate() -> dict:
    result = {}
    for symbol, value in summary.items():
        if 'gate' in value['buy_on'] or 'gate' in value['sell_on']:
            k = requests.get(GATE).json()
            for t in k:
                if t['contract'] == symbol.replace('USDT', '_USDT'):
                    result[symbol] = {
                        'volume 24H': float(t['volume_24h_base']),
                    }
    return result


get_data_binance = get_data_binance()
get_data_bybit = get_data_bybit()
get_data_bitget = get_data_bitget()
get_data_mexc = get_data_mexc()
get_data_kucoin = get_data_kucoin()
get_data_gate = get_data_gate()


def summary_volume():
    result = {}
    exchanges = {
        'binance': get_data_binance,
        'bybit': get_data_bybit,
        'bitget': get_data_bitget,
        'mexc': get_data_mexc,
        'kucoin': get_data_kucoin,
        'gate': get_data_gate,
    }
    for symbol, value in summary.items():
        buy_exchange = value['buy_on']
        sell_exchange = value['sell_on']

        buy_volume = None
        sell_volume = None
        if symbol in exchanges[buy_exchange]:
            buy_volume = exchanges[buy_exchange].get(symbol, {}).get('volume 24H')
            sell_volume = exchanges[sell_exchange].get(symbol, {}).get('volume 24H')
            result[symbol] = {
                'buy_on': value['buy_on'],
                'sell_on': value['sell_on'],
                'spread': value['spread'],
                'volume_buy_24H': buy_volume,
                'volume_sell_24H': sell_volume,
            }
    return result


# print(get_data_binance)
# print(get_data_bybit)
# print(get_data_bitget)
# print(get_data_mexc)
# print(get_data_kucoin)
# print(get_data_gate)

print(summary_volume())