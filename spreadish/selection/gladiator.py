import numpy as np
import pandas as pd
import ta
import time
import math
import logging
import ccxt
from spreadish.exchange import get_exchange

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("gladiator_selection")

exchange = get_exchange()

def sleep_rate_limit():
    try:
        ms = getattr(exchange, "rateLimit", 1000)
        time.sleep(max(ms / 1000.0, 0.05))
    except Exception:
        time.sleep(0.1)

def safe_call(fn, *a, retries=3, backoff=0.5, **kw):
    for attempt in range(1, retries + 1):
        try:
            res = fn(*a, **kw)
            sleep_rate_limit()
            return res
        except (ccxt.NetworkError, ccxt.ExchangeError, ccxt.RequestTimeout) as e:
            logger.warning("Network/Exchange error (attempt %s/%s): %s", attempt, retries, e)
            time.sleep(backoff * attempt)
        except Exception as e:
            logger.exception("Unexpected error in safe_call: %s", e)
            return None
    return None

def safe_fetch_ticker(symbol):
    return safe_call(exchange.fetch_ticker, symbol)

def safe_fetch_ohlcv(symbol, timeframe='1h', limit=100, since=None):
    return safe_call(exchange.fetch_ohlcv, symbol, timeframe, since, limit)

def safe_fetch_order_book(symbol, limit=50):
    return safe_call(exchange.fetch_order_book, symbol, limit=limit)

def calculate_rsi_safe(prices, period=14):
    if not prices or len(prices) < period:
        return None
    try:
        series = pd.Series(prices)
        rsi = ta.momentum.RSIIndicator(series, window=period).rsi().iloc[-1]
        if math.isnan(rsi):
            return None
        return float(rsi)
    except Exception as e:
        logger.debug("RSI calc error: %s", e)
        return None

def calculate_order_book_depth_safe(symbol):
    ob = safe_fetch_order_book(symbol)
    if not ob:
        return 0.0
    bids = ob.get('bids') or []
    asks = ob.get('asks') or []
    if not bids or not asks:
        return 0.0
    try:
        current_price = (bids[0][0] + asks[0][0]) / 2.0
    except Exception:
        return 0.0
    bid_depth = sum(amount for price, amount in bids if price >= current_price * 0.98)
    ask_depth = sum(amount for price, amount in asks if price <= current_price * 1.02)
    return float(bid_depth + ask_depth)

def calculate_immortal_index(stats):
    spread = max(stats.get('spread', 0), 0)
    rsi = stats.get('rsi') or 50.0
    volume = max(stats.get('volume', 0), 1.0)
    depth = max(stats.get('depth', 0), 0.0)
    volatility = max(stats.get('volatility', 0.0), 0.0)
    try:
        return (
            0.3 * (1 - spread / 5) +
            0.25 * (rsi / 100 if rsi < 70 else 0.7) +
            0.2 * np.log(volume / 1e6 + 1) +
            0.15 * (depth / 1e6) +
            0.1 * (volatility / 10)
        )
    except Exception:
        return 0.0

def get_pair_stats(symbol):
    ticker = safe_fetch_ticker(symbol)
    if not ticker:
        return None
    ohlcv = safe_fetch_ohlcv(symbol, '1h', limit=100)
    if not ohlcv or len(ohlcv) < 25:
        logger.debug("Insufficient OHLCV for %s", symbol)
        return None
    closes = [c[4] for c in ohlcv]
    volumes = [c[5] for c in ohlcv]
    try:
        bid = ticker.get('bid')
        ask = ticker.get('ask')
        if not bid or not ask or bid == 0:
            return None
        spread = ((ask - bid) / bid) * 100
        volume = sum(volumes[-24:]) if len(volumes) >= 24 else sum(volumes)
        mean_close = np.mean(closes[-24:])
        volatility = (np.std(closes[-24:]) / mean_close * 100) if mean_close != 0 else 0.0
        price_change = ((closes[-1] - closes[-24]) / closes[-24]) * 100 if closes[-24] != 0 else 0.0
        rsi = calculate_rsi_safe(closes)
        depth = calculate_order_book_depth_safe(symbol)
        immortal_index = calculate_immortal_index({
            'spread': spread,
            'rsi': rsi or 50,
            'volume': volume,
            'depth': depth,
            'volatility': volatility
        })
        return {
            'spread': spread,
            'volume': volume,
            'volatility': volatility,
            'price_change': price_change,
            'rsi': rsi or 50,
            'depth': depth,
            'immortal_index': immortal_index,
            'last_price': ticker.get('last', 0.0)
        }
    except Exception as e:
        logger.debug("Error computing stats for %s: %s", symbol, e)
        return None

def select_best_pairs(limit_markets=50, top_n=19):
    return [p[0] for p in select_best_pairs_with_stats(limit_markets, top_n)]

def select_best_pairs_with_stats(limit_markets=50, top_n=19):
    markets = safe_call(exchange.load_markets)
    if not markets:
        return []
    candidates = [s for s, m in markets.items() if s.endswith('/USDT') and m.get('active', True)]
    logger.info("Found %d candidate USDT pairs (truncating to %d)", len(candidates), limit_markets)
    candidates = candidates[:limit_markets]

    pair_scores = []
    for symbol in candidates:
        stats = get_pair_stats(symbol)
        if stats and stats['volume'] > 1e5:
            pair_scores.append((symbol, stats['immortal_index'], stats))
    pair_scores.sort(key=lambda x: x[1], reverse=True)
    return pair_scores[:top_n]
