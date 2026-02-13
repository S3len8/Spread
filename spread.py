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


bid = min_bid()
print(bid)


def max_ask():
    result = {}

    # Getting unique symbols
    all_symbols = set()

    for exchange_data in get_all_ask.values():
        all_symbols.update(exchange_data.keys())

    # For symbols get min bid
    for symbol in all_symbols:
        max_ask = float("inf")
        max_exchange = None

        for exchange, exchange_data in get_all_ask.items():
            ask = exchange_data.get(symbol)

            if ask is None:
                continue

            if ask < max_ask:
                max_ask = ask
                max_exchange = exchange

        if max_exchange:
            result[symbol] = {
                "exchange": max_exchange,
                "max_ask": max_ask
            }

    return result


ask = max_ask()
print(ask)


def spread():
    all_symbols = set(bid.keys()) | set(ask.keys())  # объединяем ключи

    for symbol in all_symbols:
        min_info = bid.get(symbol)
        max_info = ask.get(symbol)

        min_bid = min_info['min_bid'] if min_info else None
        min_exchange = min_info['exchange'] if min_info else None

        max_ask = max_info['max_ask'] if max_info else None
        max_exchange = max_info['exchange'] if max_info else None
        if min_exchange != max_exchange:
            spread = max_ask / min_bid
            print(symbol, "min_bid:", min_bid, "from", min_exchange, "| max_ask:", max_ask, "from", max_exchange, 'Spread', spread)


spread()