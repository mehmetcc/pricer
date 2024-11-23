import yfinance as yf
import logging
from typing import Dict


class StockNotFoundException(Exception):
    pass


def get_latest_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    return ticker.fast_info.last_price


def get_latest_stock_price(symbol: str, symbols: list[str]) -> float:
    if symbol not in symbols:
        raise StockNotFoundException('Stock can\'t be found')

    return get_latest_price(symbol)


def get_latest_stock_prices(symbols: list[str]) -> Dict[str, float]:
    result = dict()

    for symbol in symbols:
        try:
            price = get_latest_stock_price(symbol, symbols)
            result[symbol] = price
        except StockNotFoundException:
            logging.error(f'Stock {symbol} can\'t be found.')
        except Exception as e:
            logging.error(f'Exception occured: {e}')
    return result
