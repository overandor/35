# Spreadish

This project is a 24/7 walk-forward testing system for a hedging strategy in the cryptocurrency market. It is designed to be highly configurable and extensible, with a focus on liquidation avoidance and persistent data storage.

## Features

- **Walk-Forward Testing:** The system uses a walk-forward approach to backtesting, which provides a more realistic assessment of a strategy's performance.
- **Hedging Strategy:** The core strategy is based on hedging, with features like Dollar-Cost Averaging (DCA), taking profits on opposing positions, and avoiding losses.
- **Liquidation Avoidance:** The system includes robust mechanisms to prevent liquidations, which is a major risk in cryptocurrency trading.
- **Persistent Data Storage:** All backtesting results are saved to a persistent file, so the system can be stopped and restarted without losing its progress.
- **API Server:** The system includes an API server for entering perpetual futures positions, with support for both live and dry-run modes.
- **Data Dashboard:** A real-time data dashboard displays spread data and backtesting results.
- **Historical Entry Checking:** The system can check if a potential entry would have been successful based on historical data.
- **Hugging Face Deployment:** The project is designed to be easily deployed to Hugging Face Spaces.

## Technologies

- **Python:** The core backtesting engine and API server are written in Python.
- **FastAPI:** The API server is built with FastAPI, a modern, high-performance web framework for Python.
- **Plotly:** The data dashboard is built with Plotly, a popular data visualization library for Python.
- **Docker:** The project is containerized with Docker for easy deployment.
- **Hugging Face Spaces:** The project is designed to be deployed to Hugging Face Spaces, a platform for hosting and sharing machine learning applications.
