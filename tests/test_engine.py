import unittest
import pandas as pd
import tempfile
import os
from spreadish.backtesting.engine import BacktestingEngine, HedgingStrategy

class TestBacktestingEngine(unittest.TestCase):
    def test_run(self):
        # Create a dummy dataset.
        data = {
            'BTC_close': [10000, 11000, 12000, 11500, 13000],
        }
        data = pd.DataFrame(data, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']))

        # Create a dummy strategy with a higher take-profit threshold to ensure positions are not closed immediately.
        strategy = HedgingStrategy('BTC/USDT', take_profit_threshold=0.5)

        # Create a backtesting engine.
        engine = BacktestingEngine(strategy, data)

        # Define the walk-forward periods.
        walk_forward_periods = [
            ('2023-01-01', '2023-01-02', '2023-01-03', '2023-01-05'),
        ]

        # Run the backtest.
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_results.csv")
            results = engine.run(walk_forward_periods, filepath)

            # Check that the results are a pandas DataFrame.
            self.assertIsInstance(results, pd.DataFrame)

            # Check that the portfolio has both long and short positions.
            self.assertIn('long', engine.portfolio['positions']['BTC/USDT'])
            self.assertIn('short', engine.portfolio['positions']['BTC/USDT'])

if __name__ == '__main__':
    unittest.main()
