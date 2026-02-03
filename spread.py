from symbol import binance_funding, bybit_funding, bitget_funding, mexc_funding, no_kucoin_funding, gate_funding


def spread():
    binance = binance_funding
    bybit = bybit_funding
    bitget = bitget_funding
    mexc = mexc_funding
    kucoin = no_kucoin_funding
    gate = gate_funding
    for symbol in