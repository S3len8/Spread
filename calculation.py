import asyncio
from funding import get_summary_funding


async def calculation() -> dict:
    summary_funding = await get_summary_funding()  # New data getting
    result = {}

    for symbol, value in summary_funding.items():
        volume_buy = value['volume_buy_24H']
        volume_sell = value['volume_sell_24H']

        if volume_buy is None or volume_sell is None:
            continue

        if volume_buy > 50000 or volume_sell > 50000:
            funding_buy = value['funding buy_on'] or 0
            funding_sell = value['funding sell_on'] or 0
            spread = value['spread']

            # spread is a ratio (e.g. 1.015), convert to % before adding funding (e.g. 0.0001)
            spread_pct = (spread - 1) * 100
            funding_all = (funding_sell - funding_buy) * 100
            spread_all = spread_pct + funding_all

            result[symbol] = {
                'buy_on': value['buy_on'],
                'sell_on': value['sell_on'],
                'funding buy_on': value['funding buy_on'],
                'funding sell_on': value['funding sell_on'],
                'volume_buy_24H': volume_buy,
                'volume_sell_24H': volume_sell,
                'spread_all': spread_all,
                'spread': spread,
            }

    return result


if __name__ == '__main__':
    result = asyncio.run(calculation())
    print(result)