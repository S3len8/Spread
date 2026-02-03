import aiohttp
import asyncio
import requests


API_KEY = 'OcirhzEKhIgPDd9wcV0fOTaMMoVBq3mLY8ESmEFZXcZ53doPfPIgsSZMZVz74bSy'
API_SECRET = 'jvYQuPuM26KLvY3M67FlYtAZpCHLTf7Hc3qBhs7Ch5DPx6mxQ7mqDCwZnMywm1Sf'

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
KUCOIN_ORDER_BOOK_SECOND_API = 'https://api-futures.kucoin.com/api/v1/level2/snapshot'

GATE = 'https://api.gateio.ws/api/v4/futures/usdt/tickers'

FEES = {
    'Binance': {
        'maker:': 0.02,
        'taker:': 0.05,
    },
    'Bybit': {
        'maker:': 0.036,
        'taker:': 0.1,
    },
    'Bitget': {
        'maker:': 0.02,
        'taker:': 0.06,
    },
    'MEXC': {
        'maker:': 0.01,
        'taker:': 0.04,
    },
    'Gate': {
        'maker:': 0.02,
        'taker:': 0.05,
    },
    'Kucoin': {
        'maker:': 0.02,
        'taker:': 0.06,
    },
}


# Function for getting only symbols from Binance
def get_binance_symbol():
    url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    data = requests.get(url).json()

    result = []
    for symbol in data['symbols']:
        if symbol['contractType'] == 'PERPETUAL':
            result.append({
                'symbol': symbol['symbol'],
            })
    return result


# Function for getting only symbols from Bybit
def get_bybit_symbol():
    url = 'https://api.bybit.com/v5/market/instruments-info?category=linear&settleCoin=USDT'
    params = {'category': 'linear'}
    data = requests.get(url, params=params).json()

    result = []
    for symbol in data['result']['list']:
        if symbol['status'] == 'Trading' and symbol['contractType'] == 'LinearPerpetual':
            result.append({
                'symbol': symbol['symbol']
            })
    return result


def get_bitget_symbol():
    params = {"productType": "USDT-FUTURES"}
    data = requests.get(BITGET, params=params).json()
    result = []
    for symbol in data['data']:
        result.append({
            'symbol': symbol['symbol']
        })

    return result


def get_mexc_symbol():
    result = []
    data = requests.get(MEXC).json()
    for key in data['data']:
        symbol = key['symbol']
        result.append({
            'symbol': symbol.replace('_', '')
        })
    return result


# def get_kucoin_symbol():
#     result = []
#     data = requests.get(KUCOIN).json()
#     for key in data['data']:
#         symbol = key['symbol']
#         result.append({
#             'symbol': symbol.replace('XBT', 'BTC').replace('USDTM', 'USDT'),
#         })
#
#     return result

async def get_kucoin_symbol():
    async with aiohttp.ClientSession() as session:
        async with session.get(KUCOIN) as kucoin:
            data = await kucoin.json()

    return [{'symbol': item['symbol']} for item in data['data']]


def get_gate_symbol():
    result = []
    data = requests.get(GATE).json()
    for key in data:
        symbol = key['contract']
        result.append({
            'symbol': symbol.replace('_', ''),
        })

    return result


binance = get_binance_symbol()  # [{'symbol': 'BTCUSDT'}, {'symbol': 'ETHUSDT'}, {'symbol': 'BCHUSDT'}, {'symbol': 'XRPUSDT'}, {'symbol': 'LTCUSDT'}]
bybit = get_bybit_symbol()  # [{'symbol': '0GUSDT'}, {'symbol': '1000000BABYDOGEUSDT'}, {'symbol': '1000000CHEEMSUSDT'}, {'symbol': '1000000MOGUSDT'}]
bitget = get_bitget_symbol()  #  [{'symbol': 'BTCUSDT'}, {'symbol': 'ETHUSDT'}, {'symbol': 'XRPUSDT'}, {'symbol': 'BCHUSDT'}, {'symbol': 'LTCUSDT'}]
mexc = get_mexc_symbol()  # [{'symbol': 'BTCUSDT'}, {'symbol': 'ETHUSDT'}, {'symbol': 'SOLUSDT'}, {'symbol': 'RIVERUSDT'}, {'symbol': 'XAUTUSDT'}, {'symbol': 'BTCUSD'}, {'symbol': 'SILVERUSDT'}]
kucoin = asyncio.run(get_kucoin_symbol())  # {'BTC': 'XBTUSDTM', 'ETH': 'ETHUSDTM', 'SOL': 'SOLUSDTM', 'WIF': 'WIFUSDTM', 'PEPE': 'PEPEUSDTM', 'DOGE': 'DOGEUSDTM', 'XRP': 'XRPUSDTM', '0G': '0GUSDTM'} [{'symbol': 'XBTUSDTM'}, {'symbol': 'ETHUSDTM'}, {'symbol': 'SOLUSDTM'}, {'symbol': 'WIFUSDTM'}, {'symbol': 'PEPEUSDTM'}, {'symbol': 'DOGEUSDTM'}, {'symbol': 'XRPUSDTM'}]
gate = get_gate_symbol()  # [{'symbol': 'RAREUSDT'}, {'symbol': 'FILUSDT'}, {'symbol': 'GIGGLEUSDT'}, {'symbol': 'RECALLUSDT'}, {'symbol': 'LYNUSDT'}, {'symbol': 'SONICUSDT'}, {'symbol': 'TAUSDT'}]
# print(kucoin)


async def fetch_all_and_compare():
    kucoin = await asyncio.gather(
        get_kucoin_symbol(),
    )

    return kucoin


def normalize(symbol: str) -> str:
    return symbol.replace('USDTM', '').replace('USDT', '').replace('PERP', '').replace('USDC', '').replace('_USDT', '').replace('XBT', 'BTC').replace('USD', '').replace('_', '')


def comparison_symbols(binance: list, bybit: list, bitget: list, mexc: list, kucoin: list, gate: list) -> list:
    binance_symbol = {normalize(item['symbol']) for item in binance}
    bybit_symbol = {normalize(item['symbol']) for item in bybit}
    bitget_symbol = {normalize(item['symbol']) for item in bitget}
    mexc_symbol = {normalize(item['symbol']) for item in mexc}
    kucoin_symbol = {normalize(item['symbol']) for item in kucoin}
    gate_symbols = {normalize(item['symbol']) for item in gate}
    sets = [binance_symbol, bybit_symbol, bitget_symbol, mexc_symbol, kucoin_symbol, gate_symbols]

    return list(set().union(*sets))


kucoin = asyncio.run(fetch_all_and_compare())
kucoin_list = kucoin[0]
common_symbols = comparison_symbols(binance=binance, bybit=bybit, bitget=bitget, mexc=mexc, kucoin=kucoin_list, gate=gate)  # <class 'list'>
# print(common_symbols, len(common_symbols))  # ['INJ', 'NIL', 'DEXE', 'PTB', 'REZ', 'CHZ', 'BANANA', 'ANIME', 'ANKR', 'FLUID', 'RENDER', 'C98', 'BLUAI', 'CTK', 'PIPPIN', 'GMX', 'LINEA', 'EVAA', 'COOKIE', 'MYX', 'ENJ']


def get_spread_binance() -> dict:
    symbols_set = set(common_symbols)
    result = {}
    # Get funding
    v = requests.get(BINANCE_ORDER_BOOK).json()
    for key in v:
        symbol = key['symbol']
        if symbol.endswith('USDC'):
            continue
        if symbol.endswith('USD'):
            continue
        if symbol in symbols_set:
            continue
        symbol = key['symbol']
        result[symbol] = {
            'bid': float(key['bidPrice']),
            'ask': float(key['askPrice']),
        }
    return result


def get_spread_bybit():
    symbols_set = set(common_symbols)
    result = {}

    # список инструментов
    k = requests.get(
        BYBIT_DATA,
        params={'category': 'linear'}
    ).json()

    for t in k['result']['list']:
        symbol = t['symbol']

        if symbol.endswith(('PERP', 'USDC', 'USD')):
            continue
        if symbol in symbols_set:
            continue

        # стакан
        ob = requests.get(
            "https://api.bybit.com/v5/market/orderbook",
            params={
                "category": "linear",
                "symbol": symbol,
                "limit": 1
            }
        ).json()

        data = ob.get("result", {})
        bids = data.get("b", [])
        asks = data.get("a", [])

        if not bids or not asks:
            continue

        bid_price = bids[0]
        ask_price = asks[0]

        result[symbol] = {
            "bid": float(bid_price[0]),
            "ask": float(ask_price[0]),
        }

    return result


def get_data_bitget() -> dict:
    result = {}
    params = {"productType": "USDT-FUTURES"}
    k = requests.get(BITGET, params=params).json()
    for t in k['data']:
        result[t['symbol']] = {
            'bid': float(t['bidPr']),
            'ask': float(t['askPr']),
            'volume 24H': float(t['usdtVolume']),
        }
    return result


def get_spread_mexc():
    symbols_set = set(common_symbols)
    result = {}
    k = requests.get(MEXC).json()
    for t in k['data']:
        symbol = t['symbol']
        normalize_symbol = symbol.replace('_', '')
        if symbol.endswith('USDC'):
            continue
        if symbol.endswith('USD'):
            continue
        if normalize_symbol in symbols_set:
            continue
        result[normalize_symbol] = {
            'bid': float(t['bid1']) if 'bid1' in t else None,
            'ask': float(t['ask1']) if 'ask1' in t else None,
        }
    return result


# def get_funding_kucoin():
#     symbols_set = set(common_symbols)
#     result = {}
#     symbols = get_kucoin_symbol()
#     for item in symbols:
#         symbol = item['symbol']
#         url = f"https://api-futures.kucoin.com/api/v1/funding-rate/{symbol}/current"
#         r = requests.get(url).json()
#         data = r.get('data')
#         normalize_symbol = symbol.replace('XBT', 'BTC')
#         print(data)
#         if not data:
#             continue
#         if normalize_symbol in symbols_set:
#             continue
#         print(normalize_symbol)
#         result[normalize_symbol] = {
#             'funding': float(data['value'])
#         }
#
#         time.sleep(0.05)  # Rate limit
#
#     return result

# async def fetch_spread(session, symbol):
#     url = KUCOIN_ORDER_BOOK_SECOND_API.format()
#
#     try:
#         async with session.get(url, params={"symbol": symbol}) as r:
#             data = await r.json()
#             if data.get("code") != "200000":
#                 print(f"Warning: orderbook not available for {symbol}")
#                 return symbol, None
#
#             ob = data.get("data", {})
#             bids = ob.get("bids", [])
#             asks = ob.get("asks", [])
#
#             if not bids or not asks:
#                 return symbol, None
#
#             bid_price = bids[0]
#             ask_price = asks[0]
#
#             return symbol, {
#                 "bid": float(bid_price[0]),
#                 "ask": float(ask_price[0]),
#             }
#
#     except Exception as e:
#         print(f"Error fetching {symbol}: {e}")
#         return symbol, None
#
#
# async def get_spread_kucoin(symbols):
#     async with aiohttp.ClientSession() as session:
#         tasks = [fetch_spread(session, s) for s in symbols]
#         results = await asyncio.gather(*tasks)
#
#         # фильтруем None
#         return {
#             symbol: data
#             for symbol, data in results
#             if data is not None
#         }
#
#
# symbols = [item['symbol'] for item in kucoin_list]


# def get_data_kucoin(symbols) -> dict:
#     result = {}
#     for symbol in symbols:
#         k = requests.get(KUCOIN_ORDER_BOOK, params={"symbol": symbol}).json()
#         d = requests.get(KUCOIN, params={"symbol": symbol}).json()
#         data = k['data']
#         for c in d["data"]:
#             if c["symbol"] == symbol:
#                 volume = float(c.get("turnoverOf24h", 0))
#         result[symbol] = {
#             'bid': float(data['bestBidPrice']),
#             'ask': float(data['bestAskPrice']),
#             'volume 24H': volume,
#         }
#     return result
#
#
# symbols = [item['symbol'] for item in kucoin_list]

def get_data_kucoin(symbol: str) -> dict:
    result = {}
    symbol_kucoin = symbol.replace('BTC', 'XBT')
    k = requests.get(KUCOIN_ORDER_BOOK, params={"symbol": symbol_kucoin}).json()
    d = requests.get(KUCOIN, params={"symbol": symbol_kucoin}).json()
    data = k['data']
    for c in d["data"]:
        if c["symbol"] == symbol_kucoin:
            volume = float(c.get("turnoverOf24h", 0))
    result[symbol] = {
        'bid': float(data['bestBidPrice']),
        'ask': float(data['bestAskPrice']),
        'volume 24H': volume,
    }
    return result


symbols = [item['symbol'] for item in kucoin_list]
def symbols():
    for symbol in symbols:
        get_data_kucoin(symbol)


def get_spread_gate():
    symbols_set = set(common_symbols)
    result = {}
    data = requests.get(GATE).json()
    for key in data:
        symbol = key['contract']
        normalize_symbol = symbol.replace('_', '')
        if normalize_symbol in symbols_set:
            continue
        result[normalize_symbol] = {
            'bid': float(key['highest_bid']),
            'ask': float(key['lowest_ask']),
        }

    return result


binance_funding = get_spread_binance()  # Example print {'USDCUSDT': {'funding': 5.301e-05}, 'GRIFFAINUSDT': {'funding': 5e-05}, 'GMXUSDT': {'funding': 6.258e-05}, 'BANUSDT': {'funding': 5e-05}}
bybit_funding = get_spread_bybit()  # Example print {'0GUSDT': {'funding': -0.00062216}, '1000000BABYDOGEUSDT': {'funding': 5e-05}, '1000000CHEEMSUSDT': {'funding': 5e-05}, '1000000MOGUSDT': {'funding': -0.00065514}}
bitget_funding = get_data_bitget()   # Example print {'BTCUSDT': {'funding': 5.8e-05}, 'ETHUSDT': {'funding': 1.5e-05}, 'XRPUSDT': {'funding': 0.0001}, 'BCHUSDT': {'funding': -6.6e-05}, 'LTCUSDT': {'funding': 0.0001}}
mexc_funding = get_spread_mexc()  # Example {'BTCUSDT': {'funding': 5e-05}, 'ETHUSDT': {'funding': -0.000117}, 'SOLUSDT': {'funding': -0.000196}, 'RIVERUSDT': {'funding': -0.001273}, 'XAUTUSDT': {'funding': 5e-05}}
# kucoin_funding = asyncio.run(get_spread_kucoin(symbols))  # Example {'BTCUSDT': {'funding': -7e-06}, 'ETHUSDT': {'funding': -5.5e-05}, 'SOLUSDT': {'funding': -2.8e-05}, 'WIFUSDT': {'funding': -3e-06}, 'PEPEUSDT': {'funding': -2.2e-05}}  {'XBTUSDTM': {'funding': -7e-06}, 'ETHUSDTM': {'funding': 1.3e-05}, 'SOLUSDTM': {'funding': -3e-06}, 'WIFUSDTM': {'funding': 0.000173}, 'PEPEUSDTM': {'funding': -0.000166}}
gate_funding = get_spread_gate()  # Example {'DOTUSDT': {'funding': -0.00012}, '人生K线USDT': {'funding': 5e-05}, 'IMXUSDT': {'funding': 5e-05}, 'USUALUSDT': {'funding': 1.2e-05}, 'EPICUSDT': {'funding': -0.00166}, 'IPUSDT': {'funding': 1.2e-05}}
kucoin_funding = get_data_kucoin(symbols)
no_kucoin_funding = {k.replace('USDTM', 'USDT').replace('XBT', 'BTC'): v for k, v in kucoin_funding.items()}  # Need for converting symbols ETHUSDTM to ETHUSDT
# print(binance_funding)
# print(bybit_funding)
# print(bitget_funding)
# # print(mexc_funding)
# print(kucoin_funding)
# print(gate_funding)
# print(no_kucoin_funding)
# set_all_symbols_funding = set().union(binance_funding, bybit_funding, bitget_funding, mexc_funding, no_kucoin_funding, gate_funding)
# print(set_all_symbols_funding, len(set_all_symbols_funding))
source_data = {
    'binance': binance_funding,
    'bybit': bybit_funding,
    'bitget': bitget_funding,
    'mexc': mexc_funding,
    'kucoin': symbols(),
    'gate': gate_funding,
}
print(source_data)