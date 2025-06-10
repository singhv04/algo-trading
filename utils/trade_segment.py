# ---------------------------
# File: utils/trade_segment.py
# ---------------------------

import pandas as pd

def get_trade_segment(df, trade):
    """
    Returns the subset of candle dataframe between entry and exit time.
    """
    return df[(df['timestamp'] >= trade['entry_time']) & (df['timestamp'] <= trade['exit_time'])].copy()

def determine_indicators_used(trade):
    """
    Infers which indicators contributed to the trade signal.
    """
    used = []
    if trade['direction'] == 'buy':
        if trade['rsi'] < 30: used.append('RSI')
        if trade['macd'] > trade['signal_line']: used.append('MACD')
        if trade['+DI'] > trade['-DI']: used.append('DMI')
        if trade['divergence'] == 'bullish': used.append('Divergence')
    elif trade['direction'] == 'short':
        if trade['rsi'] > 70: used.append('RSI')
        if trade['macd'] < trade['signal_line']: used.append('MACD')
        if trade['-DI'] > trade['+DI']: used.append('DMI')
        if trade['divergence'] == 'bearish': used.append('Divergence')
    return used

def resample_trade_segment(df, interval):
    """
    Resamples OHLCV + numeric indicators to a new interval (e.g., 1H).
    """
    df = df.set_index('timestamp')
    ohlcv = df[['open', 'high', 'low', 'close', 'volume']].resample(interval).agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
    })
    numeric = df.select_dtypes(include='number').drop(columns=['open', 'high', 'low', 'close', 'volume'], errors='ignore')
    indicators = numeric.resample(interval).mean()
    combined = pd.concat([ohlcv, indicators], axis=1).dropna().reset_index()
    return combined
