import yfinance as yf
import pandas as pd

def get_prices(tickers):
    data = yf.download(tickers, period="6mo")["Close"]
    return data


