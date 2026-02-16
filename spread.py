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
# print(get_all_bid)


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
# print(get_all_ask)


def min_bid():
    result = {}

    all_symbols = set()

    for exchange_data in get_all_bid.values():
        all_symbols.update(exchange_data.keys())

    for symbol in all_symbols:
        min_value = float("inf")
        min_exchange = None

        for exchange, exchange_data in get_all_bid.items():
            bid = exchange_data.get(symbol)

            if bid is None:
                continue

            if bid < min_value:
                min_value = bid
                min_exchange = exchange

        if min_exchange is not None:
            result[symbol] = {
                "exchange": min_exchange,
                "min_bid": min_value
            }

    return result


bid = min_bid()
print(bid)


def max_ask():
    result = {}

    all_symbols = set()

    for exchange_data in get_all_ask.values():
        all_symbols.update(exchange_data.keys())

    for symbol in all_symbols:
        max_value = float("-inf")
        max_exchange = None

        for exchange, exchange_data in get_all_ask.items():
            ask = exchange_data.get(symbol)

            if ask is None:
                continue

            if ask > max_value:
                max_value = ask
                max_exchange = exchange

        if max_exchange is not None:
            result[symbol] = {
                "exchange": max_exchange,
                "max_ask": max_value
            }

    return result


ask = max_ask()
print(ask)


def spread():
    result = {}

    all_symbols = set()

    for exchange_data in get_all_bid.values():
        all_symbols.update(exchange_data.keys())

    for symbol in all_symbols:
        min_ask = float("inf")
        max_bid = float("-inf")

        min_ask_exchange = None
        max_bid_exchange = None

        for exchange in get_all_bid.keys():
            bid = get_all_bid[exchange].get(symbol)
            ask = get_all_ask[exchange].get(symbol)

            if bid is not None and bid > max_bid:
                max_bid = bid
                max_bid_exchange = exchange

            if ask is not None and ask < min_ask:
                min_ask = ask
                min_ask_exchange = exchange

        # Need for don`t get same exchanges
        if (
            min_ask_exchange
            and max_bid_exchange
            and min_ask_exchange != max_bid_exchange
            and min_ask != 0
        ):
            result[symbol] = {
                "buy_on": min_ask_exchange,
                "sell_on": max_bid_exchange,
                "min_ask": min_ask,
                "max_bid": max_bid,
                "spread_ratio": max_bid / min_ask
            }

    return result


spread = spread()

for symbol, data in spread.items():
    print(symbol, data)


# spread_data = spread()
# print(spread_data)

def spread_ratio():
    result = {}
    for symbol, value in spread.items():
        if value['spread_ratio'] > 1.012:
            result[symbol] = {
                'spread': value['spread_ratio']
            }

    return result


spread_ratio = spread_ratio()
print(spread_ratio)


def summary():
    result = {}
    for symbol in spread_ratio.keys() & spread.keys():
        result[symbol] = {

        }