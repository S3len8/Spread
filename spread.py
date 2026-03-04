from symbol import get_source_data


SPREAD_FILTER_MIN = 1.012
SPREAD_FILTER_MAX = 5.000


def get_all_bid(source_data, binance_funding, bitget_funding, mexc_funding, gate_funding):
    bybit_spread = source_data['bybit']
    kucoin_spread = source_data['kucoin']
    return {
        'binance': {s: v['bid'] for s, v in binance_funding.items()},
        'bybit':   {s: v['bid'] for s, v in bybit_spread.items()},
        'bitget':  {s: v['bid'] for s, v in bitget_funding.items()},
        'mexc':    {s: v['bid'] for s, v in mexc_funding.items() if v['bid'] is not None},
        'kucoin':  {s: v['bid'] for s, v in kucoin_spread.items()},
        'gate':    {s: v['bid'] for s, v in gate_funding.items()},
    }


def get_all_ask(source_data, binance_funding, bitget_funding, mexc_funding, gate_funding):
    bybit_spread = source_data['bybit']
    kucoin_spread = source_data['kucoin']
    return {
        'binance': {s: v['ask'] for s, v in binance_funding.items()},
        'bybit':   {s: v['ask'] for s, v in bybit_spread.items()},
        'bitget':  {s: v['ask'] for s, v in bitget_funding.items()},
        'mexc':    {s: v['ask'] for s, v in mexc_funding.items() if v['ask'] is not None},
        'kucoin':  {s: v['ask'] for s, v in kucoin_spread.items()},
        'gate':    {s: v['ask'] for s, v in gate_funding.items()},
    }


def get_spread(all_bid, all_ask):
    result = {}
    all_symbols = set()
    for exchange_data in all_bid.values():
        all_symbols.update(exchange_data.keys())

    for symbol in all_symbols:
        min_ask = float("inf")
        max_bid = float("-inf")
        min_ask_exchange = None
        max_bid_exchange = None

        for exchange in all_bid.keys():
            bid = all_bid[exchange].get(symbol)
            ask = all_ask[exchange].get(symbol)

            if bid is not None and bid > max_bid:
                max_bid = bid
                max_bid_exchange = exchange

            if ask is not None and ask < min_ask:
                min_ask = ask
                min_ask_exchange = exchange

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


# async — call async get_source_data()
async def get_summary() -> dict:
    source_data, binance_funding, bitget_funding, mexc_funding, gate_funding = await get_source_data()

    all_bid = get_all_bid(source_data, binance_funding, bitget_funding, mexc_funding, gate_funding)
    all_ask = get_all_ask(source_data, binance_funding, bitget_funding, mexc_funding, gate_funding)
    spread = get_spread(all_bid, all_ask)

    result = {}
    for symbol, value in spread.items():
        if value['spread_ratio'] > SPREAD_FILTER_MIN and value['spread_ratio'] < SPREAD_FILTER_MAX:
            result[symbol] = {
                'buy_on': value['buy_on'],
                'sell_on': value['sell_on'],
                'spread': value['spread_ratio']
            }
    return result
