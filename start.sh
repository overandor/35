#!/bin/bash

# Start the API server in the background.
uvicorn spreadish.api.main:app --host 0.0.0.0 --port 80 &

# Start the backtesting script in the background.
python run_backtest.py &

# Start the dashboard in the foreground.
python run_dashboard.py
