import ccxt
import os

def get_exchange():
    """
    Returns an authenticated ccxt exchange instance.
    """
    return ccxt.gateio({
        'apiKey': os.getenv("GATE_API_KEY"),
        'secret': os.getenv("GATE_API_SECRET"),
        'enableRateLimit': True,
    })
