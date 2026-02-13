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
    result = {}

    # Getting unique symbols
    all_symbols = set()

    for exchange_data in get_all_bid.values():
        all_symbols.update(exchange_data.keys())

    # For symbols get min bid
    for symbol in all_symbols:
        min_bid = float("inf")
        min_exchange = None

        for exchange, exchange_data in get_all_bid.items():
            bid = exchange_data.get(symbol)

            if bid is None:
                continue

            if bid < min_bid:
                min_bid = bid
                min_exchange = exchange

        if min_exchange:
            result[symbol] = {
                "exchange": min_exchange,
                "min_bid": min_bid
            }

    return result


min_bid = min_bid()
print(min_bid)


def spread():
    pass