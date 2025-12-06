import pandas as pd
from spreadish.exchange import get_exchange

exchange = get_exchange()

def fetch_ohlcv(symbol, timeframe='1d', limit=100, since=None):
    """
    Fetches historical OHLCV data for a given symbol.

    Args:
        symbol: The symbol to fetch data for.
        timeframe: The timeframe to fetch data for.
        limit: The number of data points to fetch.
        since: The start date in UTC milliseconds.

    Returns:
        A pandas DataFrame with the OHLCV data.
    """
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit, since=since)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df.rename(columns={'close': f'{symbol.split("/")[0]}_close'}, inplace=True)
    return df
