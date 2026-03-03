import requests
from symbol import BINANCE_MIN_SIZE


def get_minQty_stepSize_binance(symbols: list) -> dict:
    """
    Function for getting minQty and stepSize for coins after calculation
    Need for second check and compare symbols
    """
    result = {}
    data = requests.get(BINANCE_MIN_SIZE).json()
    for k in data['symbols']:
        for symbol in symbols:  # For each symbol in list
            if symbol == k['symbol']:
                filters = k.get('filters')
                if filters[2]['filterType'] == 'MARKET_LOT_SIZE':
                    minQty = filters[2]['minQty']
                    stepSize = filters[2]['stepSize']
                    result[symbol] = {
                        'minQty': minQty,
                        'stepQty': stepSize,
                    }
    return result


def get_symbols_calculation() -> dict:
    """
    Second compare all symbols and control spreads
    """
    symbols = ['FUNUSDT', 'BTCUSDT']
    contracts = get_minQty_stepSize_binance(symbols)
    return contracts


def compare_symbols():
    pass


if __name__ == '__main__':
    print(get_symbols_calculation())