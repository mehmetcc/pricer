from typing import Dict
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from .resolver import get_latest_stock_prices, get_symbols_by_client_id, set_symbol_by_client_id


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


@app.websocket('/api/v1/ws')
async def prices(websocket: WebSocket) -> None:
    await websocket.accept()
    logging.info("WebSocket connection accepted.")

    client_id = websocket.headers.get('X-Client-Id')
    if not client_id:
        await websocket.close(code=1008)
        logging.error("Missing X-Client-Id header.")
        return

    async def receive_messages():
        """Receive stock symbols from the client."""
        while True:
            try:
                data = await websocket.receive_text()
                symbols = await get_symbols_by_client_id(client_id)
                if data not in symbols:
                    await set_symbol_by_client_id(data, client_id)
                    logging.info(f"Added stock symbol: {data}")
                    await websocket.send_text(f"Tracking stock: {data}")
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
