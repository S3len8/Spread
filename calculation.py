import requests
import asyncio
import aiohttp
from symbol import FEES
from funding import summary_funding


def calculation():
    result = {}
    for symbol, value in summary_funding.items():
        volume_buy = value['volume_buy_24H']
        volume_sell = value['volume_sell_24H']
        if volume_buy > 150000 or volume_sell > 150000:
            funding_buy = 0 if value['funding buy_on'] is None else value['funding buy_on']
            funding_sell = 0 if value['funding sell_on'] is None else value['funding sell_on']
            spread = value['spread']
            if funding_buy > 0 and funding_sell > 0:
                funding_all = funding_sell - funding_buy
                spread_all = spread + funding_all
            if funding_buy > 0 and funding_sell < 0:
                funding_all = funding_buy + funding_sell
                spread_all = spread + funding_all
            if funding_buy < 0 and funding_sell > 0:
                funding_all = funding_sell - funding_buy
                spread_all = spread + funding_all
            if funding_buy < 0 and funding_sell < 0:
                funding_all = funding_sell + funding_buy
                spread_all = spread + funding_all
            result[symbol] = {
                'buy_on': value['buy_on'],
                'sell_on': value['sell_on'],
                'funding buy_on': value['funding buy_on'],
                'funding sell_on': value['funding sell_on'],
                'volume_buy_24H': value['volume_buy_24H'],
                'volume_sell_24H': value['volume_sell_24H'],
                'spread_all': spread_all,
                'spread': spread
            }
    return result


if __name__ == '__main__':
    calculation = calculation()
    print(calculation)