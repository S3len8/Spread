from symbol import binance_funding, bitget_funding, mexc_funding, gate_funding, source_data


def min_bid():
    binance = {
        symbol: value['bid']
        for symbol, value in binance_funding.items()
    }

    return {
        'binance': binance,
    }


min_bid = min_bid()
print(min_bid)


def max_ask():
    pass


def spread():
    binance = binance_funding
    bybit = source_data['bybit']
    bitget = bitget_funding
    mexc = mexc_funding
    kucoin = source_data['kucoin']
    gate = gate_funding