import datetime as dt
import json
import time
from threading import Thread
from typing import Union

from websocket import create_connection

TIMEOUT = 3600

coins = [
    'xrpusdt',
    'btcusdt',
    'ethusdt',
]


# Parse websocket data into two values: coin, close_price
def parse_ws(result: Union[str, bytes, bytearray]) -> tuple[str, float]:
    msg = json.loads(result)
    return str(msg['s']), float(msg['c'])


# Class assigned to each coin after threading.
class CoinData:
    def __init__(self, pair: str, now: float):
        self._coin: str = pair
        self._price: float = 1
        self._now: float = now
        self._max_price: float = 0
        self._prices_list: list = []
        self._all_prices: list = []


# Function for thread processes
def coin_thread(c: str) -> None:
    ws = create_connection(
        'wss://stream.binance.com:9443/ws/' + c + '@miniTicker'
    )
    start = time.time()
    coin = CoinData(c, start)

    # Create infinite loop
    while True:
        try:
            coin._now = time.time()
            result = ws.recv()
            coin._coin, coin._price = parse_ws(result)
            coin._prices_list.append((coin._price, coin._now))
            if coin._now - coin._prices_list[0][1] >= TIMEOUT:
                coin._prices_list.pop(0)
            for el in coin._prices_list:
                coin._all_prices.append(el[0])

            coin._max_price = max(coin._all_prices)

            if coin._price < coin._max_price * 0.99:
                print(
                    dt.datetime.now().strftime('%H:%M:%S'),
                    f'The price {coin._price} of {coin._coin} futures has '
                    f'fallen by 1% from the maximum price {coin._max_price} '
                    'for the last hour!',
                )

        except Exception as e:
            print(e)
            break


# Crank it up
if __name__ == "__main__":
    first_run_flag = 0
    [
        Thread(
            target=coin_thread,
            args=(str(coin),),
        ).start()
        for coin in coins
    ]
