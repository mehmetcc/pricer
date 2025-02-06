import yfinance as yf
import logging
from typing import Dict

from .redis import get_symbols, set_symbol


class StockNotFoundException(Exception):
    pass


async def get_symbols_by_client_id(client_id: str) -> list[str]:
    symbols = await get_symbols(client_id)
    return symbols


async def set_symbol_by_client_id(stock: str, client_id: str) -> None:
    await set_symbol(stock, client_id)


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


def check_if_valid_symbol(symbol: str) -> bool:
    try:
        get_latest_price(symbol)
        return True
    except:
        return False
