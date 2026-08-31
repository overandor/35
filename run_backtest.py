import time
import os
import pandas as pd
import logging
from spreadish.selection.gladiator import select_best_pairs
from spreadish.data.fetcher import fetch_ohlcv
from spreadish.backtesting.engine import BacktestingEngine, HedgingStrategy

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("backtester")

def main():
    """
    The main entry point for the continuous backtesting engine.
    """
    while True:
        try:
            # Select the best pairs to trade.
            pairs = select_best_pairs()

            for pair in pairs:
                # Define the path to the historical data file.
                data_filepath = f"data/{pair.replace('/', '_')}.csv"

                # Check if the historical data file exists.
                if os.path.exists(data_filepath):
                    # If the file exists, load the existing data.
                    data = pd.read_csv(data_filepath, index_col='timestamp', parse_dates=True)

                    # Fetch only the new data.
                    latest_timestamp = data.index[-1]
                    new_data = fetch_ohlcv(pair, timeframe='1h', since=int(latest_timestamp.timestamp() * 1000))

                    # Append the new data to the existing data.
                    data = pd.concat([data, new_data])
                else:
                    # If the file doesn't exist, fetch the full history.
                    data = fetch_ohlcv(pair, timeframe='1h')

                # Save the updated data to the file.
                os.makedirs('data', exist_ok=True)
                data.to_csv(data_filepath)

                # Create the trading strategy.
                strategy = HedgingStrategy(pair)

                # Create the backtesting engine.
                engine = BacktestingEngine(strategy, data)

                # Define the walk-forward periods.
                train_size = int(len(data) * 0.7)
                test_size = int(len(data) * 0.1)
                step_size = int(len(data) * 0.1)

                walk_forward_periods = []
                for i in range(0, len(data) - train_size - test_size, step_size):
                    train_start = data.index[i]
                    train_end = data.index[i + train_size]
                    test_start = data.index[i + train_size + 1]
                    test_end = data.index[i + train_size + test_size]
                    walk_forward_periods.append((train_start, train_end, test_start, test_end))

                # Run the backtest.
                engine.run(walk_forward_periods, f"backtesting_results_{pair.replace('/', '_')}.csv")

            # Wait for the next iteration.
            time.sleep(60 * 60)  # Sleep for one hour.
        except Exception as e:
            logger.exception("An error occurred: %s", e)
            time.sleep(60) # Wait for a minute before retrying

if __name__ == '__main__':
    main()
