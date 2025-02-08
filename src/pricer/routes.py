from typing import Dict
from fastapi import FastAPI, Header, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from .resolver import *
from pydantic import BaseModel


origins = [
    "http://localhost:3000"
]


app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)


@app.get('/')
async def root() -> Dict[str, str]:
    return {'message': 'I am running, against all odds'}


@app.get('/symbol')
async def get_symbol(client_id: str = Header(None, alias="X-Client-ID")) -> list[str]:
    return await get_symbols_by_client_id(client_id)


class StockSymbol(BaseModel):
    symbol: str


@app.post('/symbol')
async def add_symbol(stock: StockSymbol, client_id: str = Header(None, alias="X-Client-ID")) -> None:
    check = check_if_valid_symbol(stock.symbol)

    if check:
        symbols = await get_symbols_by_client_id(client_id)
        if stock.symbol not in symbols:
            await set_symbol_by_client_id(stock.symbol, client_id)
            return {"message": f"Symbol {stock.symbol} added for client {client_id}"}
        return {"message": f"Symbol {stock.symbol} already exists for client {client_id}"}
    else:
        from fastapi import HTTPException, Header
        raise HTTPException(
            status_code=400, detail=f"Invalid stock symbol: {stock.symbol}")


@app.delete('/symbol')
async def delete_symbol(stock: StockSymbol, client_id: str = Header(None, alias="X-Client-ID")) -> None:
    await delete_symbol_by_client_id(stock.symbol, client_id)
    return {"message": f"Symbol {stock.symbol} deleted for client {client_id}"}


@app.websocket('/api/v1/ws')
async def prices(websocket: WebSocket) -> None:
    await websocket.accept()

    client_id = websocket.headers.get('X-Client-ID')
    if not client_id:
        await websocket.close(code=1008)
        logging.error("Missing X-Client-ID header.")
        return
    logging.info(f"WebSocket connection accepted for client {client_id}.")

    async def receive_messages():
        """Receive stock symbols from the client."""
        while True:
            try:
                data = await websocket.receive_text()
                check = check_if_valid_symbol(data)

                if check:
                    symbols = await get_symbols_by_client_id(client_id)
                    if data not in symbols:
                        await set_symbol_by_client_id(data, client_id)
                        logging.info(f"Added stock symbol: {data}")
                        await websocket.send_text(f"Tracking stock: {data}")
                else:
                    logging.error(f"Invalid stock symbol: {data}")
                    await websocket.send_text(f"Invalid stock symbol: {data}")
            except Exception as e:
                logging.error(f"Error receiving message: {e}")
                break

    async def send_prices():
        """Stream stock prices to the client every 10 seconds."""
        while True:
            try:
                symbols = await get_symbols_by_client_id(client_id)
                if symbols:
                    # Send latest stock prices for tracked symbols
                    stock_prices = get_latest_stock_prices(symbols)
                    logging.info(f"Sending stock prices: {stock_prices}")
                    await websocket.send_json(stock_prices)
                await asyncio.sleep(10)
            except Exception as e:
                logging.error(f"Error sending stock prices: {e}")
                break

    # Run both tasks concurrently
    receive_task = asyncio.create_task(receive_messages())
    send_task = asyncio.create_task(send_prices())

    await asyncio.gather(receive_task, send_task)
    logging.info("WebSocket connection closed.")
