from symbol import binance_funding, bitget_funding, mexc_funding, gate_funding, source_data

bybit_spread = source_data['bybit']
kucoin_spread = source_data['kucoin']


def get_all_bid():
    binance = {
        symbol: value['bid']
        for symbol, value in binance_funding.items()
    }
    bybit = {
        symbol: value['bid']
        for symbol, value in bybit_spread.items()
    }
    bitget = {
        symbol: value['bid']
        for symbol, value in bitget_funding.items()
    }
    mexc = {
        symbol: value['bid']
        for symbol, value in mexc_funding.items()
    }
    kucoin = {
        symbol: value['bid']
        for symbol, value in kucoin_spread.items()
    }
    gate = {
        symbol: value['bid']
        for symbol, value in gate_funding.items()
    }

    return {
        'binance': binance,
        'bybit': bybit,
        'bitget': bitget,
        'mexc': mexc,
        'kucoin': kucoin,
        'gate': gate,
    }


get_all_bid = get_all_bid()
print(get_all_bid)


def get_all_ask():
    binance = {
        symbol: value['ask']
        for symbol, value in binance_funding.items()
    }
    bybit = {
        symbol: value['ask']
        for symbol, value in bybit_spread.items()
    }
    bitget = {
        symbol: value['ask']
        for symbol, value in bitget_funding.items()
    }
    mexc = {
        symbol: value['ask']
        for symbol, value in mexc_funding.items()
    }
    kucoin = {
        symbol: value['ask']
        for symbol, value in kucoin_spread.items()
    }
    gate = {
        symbol: value['ask']
        for symbol, value in gate_funding.items()
    }

    return {
        'binance': binance,
        'bybit': bybit,
        'bitget': bitget,
        'mexc': mexc,
        'kucoin': kucoin,
        'gate': gate,
    }


get_all_ask = get_all_ask()
print(get_all_ask)


def min_bid():
    for exchange, value in get_all_bid.items():
        for symbol, bid in value.items():
            binance = bid
            print(binance)


min_bid = min_bid()
print(min_bid)


def spread():
    pass