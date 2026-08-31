import pandas as pd
import os
import numpy as np

class HedgingStrategy:
    """
    This class implements a hedging strategy for perpetual futures.
    """

    def __init__(self, symbol, dca_levels=5, take_profit_threshold=0.05):
        self.symbol = symbol
        self.dca_levels = dca_levels
        self.take_profit_threshold = take_profit_threshold

    def train(self, data):
        """
        Analyzes the training data to determine the optimal take-profit threshold.
        """
        # Calculate the average true range (ATR) of the training data.
        high_low = data[f'{self.symbol.split("/")[0]}_high'] - data[f'{self.symbol.split("/")[0]}_low']
        high_close = np.abs(data[f'{self.symbol.split("/")[0]}_high'] - data[f'{self.symbol.split("/")[0]}_close'].shift())
        low_close = np.abs(data[f'{self.symbol.split("/")[0]}_low'] - data[f'{self.symbol.split("/")[0]}_close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]

        # Set the take-profit threshold to a multiple of the ATR.
        self.take_profit_threshold = atr / data[f'{self.symbol.split("/")[0]}_close'].iloc[-1] * 2

    def on_data(self, timestamp, row, portfolio):
        current_price = row[f'{self.symbol.split("/")[0]}_close']

        if self.symbol not in portfolio['positions']:
            self.open_long(portfolio, current_price, 1)
            self.open_short(portfolio, current_price, 1)
            return

        pos = portfolio['positions'][self.symbol]
        if 'long' not in pos or 'short' not in pos:
            return

        if current_price > pos['long']['entry_price'] * (1 + self.take_profit_threshold):
            self.close_all_positions(portfolio, current_price)
            return

        elif current_price < pos['short']['entry_price'] * (1 - self.take_profit_threshold):
            self.close_all_positions(portfolio, current_price)
            return

        if pos['long']['contracts'] < self.dca_levels and \
           current_price < pos['long']['entry_price'] * (1 - pos['long']['contracts'] * 0.01):
            self.open_long(portfolio, current_price, 1)

        elif pos['short']['contracts'] < self.dca_levels and \
             current_price > pos['short']['entry_price'] * (1 + pos['short']['contracts'] * 0.01):
            self.open_short(portfolio, current_price, 1)

    def open_long(self, portfolio, price, contracts):
        if self.symbol not in portfolio['positions'] or 'long' not in portfolio['positions'][self.symbol]:
            portfolio['positions'][self.symbol] = portfolio['positions'].get(self.symbol, {})
            portfolio['positions'][self.symbol]['long'] = {'contracts': 0, 'entry_price': 0}

        pos = portfolio['positions'][self.symbol]['long']
        new_total_contracts = pos['contracts'] + contracts
        new_total_value = (pos['entry_price'] * pos['contracts']) + (price * contracts)
        pos['entry_price'] = new_total_value / new_total_contracts
        pos['contracts'] = new_total_contracts

    def open_short(self, portfolio, price, contracts):
        if self.symbol not in portfolio['positions'] or 'short' not in portfolio['positions'][self.symbol]:
            portfolio['positions'][self.symbol] = portfolio['positions'].get(self.symbol, {})
            portfolio['positions'][self.symbol]['short'] = {'contracts': 0, 'entry_price': 0}

        pos = portfolio['positions'][self.symbol]['short']
        new_total_contracts = pos['contracts'] + contracts
        new_total_value = (pos['entry_price'] * pos['contracts']) + (price * contracts)
        pos['entry_price'] = new_total_value / new_total_contracts
        pos['contracts'] = new_total_contracts

    def close_all_positions(self, portfolio, current_price):
        if self.symbol in portfolio['positions']:
            pos = portfolio['positions'][self.symbol]
            pnl = 0
            if 'long' in pos:
                pnl += (current_price - pos['long']['entry_price']) * pos['long']['contracts']
            if 'short' in pos:
                pnl += (pos['short']['entry_price'] - current_price) * pos['short']['contracts']

            portfolio['margin'] += pnl
            del portfolio['positions'][self.symbol]


class BacktestingEngine:
    def __init__(self, strategy, data, initial_capital=10000, leverage=10):
        self.strategy = strategy
        self.data = data
        self.initial_capital = initial_capital
        self.leverage = leverage
        self.portfolio = {
            'margin': initial_capital,
            'positions': {}
        }
        self.results = []

    def run(self, walk_forward_periods, results_filepath):
        for train_start, train_end, test_start, test_end in walk_forward_periods:
            training_data = self.data.loc[train_start:train_end]
            self.strategy.train(training_data)

            testing_data = self.data.loc[test_start:test_end]
            for timestamp, row in testing_data.iterrows():
                self.strategy.on_data(timestamp, row, self.portfolio)
                self.results.append({
                    'timestamp': timestamp,
                    'portfolio_value': self.calculate_portfolio_value(row)
                })

        results_df = pd.DataFrame(self.results)
        if os.path.exists(results_filepath):
            existing_results_df = pd.read_csv(results_filepath, index_col=0)
            results_df = pd.concat([existing_results_df, results_df])
        results_df.to_csv(results_filepath)

        return results_df

    def calculate_portfolio_value(self, current_row):
        unrealized_pnl = 0
        for symbol, position in self.portfolio['positions'].items():
            price = current_row[f'{symbol.split("/")[0]}_close']
            if 'long' in position:
                unrealized_pnl += (price - position['long']['entry_price']) * position['long']['contracts']
            if 'short' in position:
                unrealized_pnl += (position['short']['entry_price'] - price) * position['short']['contracts']

        return self.portfolio['margin'] + unrealized_pnl
