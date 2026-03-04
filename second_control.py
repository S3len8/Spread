import requests
from symbol import BINANCE_MIN_SIZE, BYBIT_MIN_SIZE, BITGET_MIN_SIZE, MEXC_MIN_SIZE, KUCOIN_MIN_SIZE, GATE_MIN_SIZE


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


def get_minQty_stepSize_bybit(symbols: list) -> dict:
    """
    Function for getting minQty and stepSize for coins after calculation
    Need for second check and compare symbols
    """
    symbols_set = set(symbols)
    result = {}
    data = requests.get(BYBIT_MIN_SIZE).json()
    for one_symbol in data['result']['list']:
        symbol = one_symbol['symbol']
        if symbol in symbols_set:
            minQty = one_symbol['lotSizeFilter']['minOrderQty']
            stepSize = one_symbol['lotSizeFilter']['qtyStep']
            result[symbol] = {
                'minQty': minQty,
                'stepQty': stepSize,
            }
    return result


def get_minQty_stepSize_bitget(symbols: list) -> dict:
    """
    Function for getting minQty and stepSize for coins after calculation
    Need for second check and compare symbols
    """
    symbols_set = set(symbols)
    result = {}
    data = requests.get(BITGET_MIN_SIZE).json()
    for one_symbol in data['data']:
        symbol = one_symbol['symbol']
        if symbol in symbols_set:
            minQty = one_symbol['minTradeNum']
            stepSize = one_symbol['sizeMultiplier']
            result[symbol] = {
                'minQty': minQty,
                'stepQty': stepSize,
            }
    return result


def get_minQty_stepSize_mexc(symbols: list) -> dict:
    """
    Function for getting minQty and stepSize for coins after calculation
    Need for second check and compare symbols
    """
    symbols_set = set(symbols)
    result = {}
    data = requests.get(MEXC_MIN_SIZE).json()
    for one_symbol in data['data']:
        symbol = one_symbol['symbol']
        normalized_symbol = symbol.replace('_USDT', 'USDT')
        if normalized_symbol in symbols_set:
            minQty = one_symbol['contractSize']
            stepSize = one_symbol['contractSize']  # Don`t found step size for mexc
            result[normalized_symbol] = {
                'minQty': minQty,
                'stepQty': stepSize,
            }
    return result


def get_symbols_calculation() -> dict:
    """
    Second compare all symbols and control spreads
    """
    symbols = ['FUNUSDT', 'BTCUSDT']
    contracts_binance = get_minQty_stepSize_binance(symbols)
    contracts_bybit = get_minQty_stepSize_bybit(symbols)
    contracts_bitget = get_minQty_stepSize_bitget(symbols)
    contracts_mexc = get_minQty_stepSize_mexc(symbols)
    return f' binance: {contracts_binance}, bybit: {contracts_bybit}, bitget: {contracts_bitget}, mexc: {contracts_mexc}'


def compare_symbols():
    pass


if __name__ == '__main__':
    print(get_symbols_calculation())