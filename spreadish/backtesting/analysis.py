import pandas as pd

def check_historical_entry(data, symbol, entry_timestamp, entry_price, side, take_profit_threshold, stop_loss_threshold):
    """
    Checks if a potential entry would have been successful based on historical data.

    Args:
        data: The historical market data.
        symbol: The symbol of the asset.
        entry_timestamp: The timestamp of the potential entry.
        entry_price: The price of the potential entry.
        side: 'buy' or 'sell'.
        take_profit_threshold: The take profit threshold.
        stop_loss_threshold: The stop loss threshold.

    Returns:
        A dictionary with the result of the check.
    """
    # Find the data after the entry timestamp.
    future_data = data.loc[entry_timestamp:]
    base_currency = symbol.split('/')[0]

    for timestamp, row in future_data.iterrows():
        current_price = row[f'{base_currency}_close']

        if side == 'buy':
            # Check for take profit.
            if current_price >= entry_price * (1 + take_profit_threshold):
                return {'successful': True, 'exit_price': current_price, 'exit_timestamp': timestamp}

            # Check for stop loss.
            elif current_price <= entry_price * (1 - stop_loss_threshold):
                return {'successful': False, 'exit_price': current_price, 'exit_timestamp': timestamp}

        elif side == 'sell':
            # Check for take profit.
            if current_price <= entry_price * (1 - take_profit_threshold):
                return {'successful': True, 'exit_price': current_price, 'exit_timestamp': timestamp}

            # Check for stop loss.
            elif current_price >= entry_price * (1 + stop_loss_threshold):
                return {'successful': False, 'exit_price': current_price, 'exit_timestamp': timestamp}

    return {'successful': None, 'reason': 'Trade did not close within the given data.'}
