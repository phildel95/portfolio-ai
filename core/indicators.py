import numpy as np
import pandas as pd

def moving_average(series, window=20):
    return series.rolling(window).mean()

def trend_score(series):
    ma20 = moving_average(series, 20)
    ma50 = moving_average(series, 50)

    if series.iloc[-1] > ma20.iloc[-1] > ma50.iloc[-1]:
        return 1  # haussier
    elif series.iloc[-1] < ma20.iloc[-1] < ma50.iloc[-1]:
        return -1  # baissier
    return 0  # neutre

def volatility(series):
    return series.pct_change().std() * 100


