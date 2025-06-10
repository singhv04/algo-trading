from indicators.ema import calculate_ema

def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    Calculates MACD and signal line and histogram.

    MACD = EMA_fast - EMA_slow
    Signal = EMA of MACD line
    Histogram = MACD - Signal

    Parameters:
        df (pd.DataFrame): DataFrame with 'close' column
        fast (int): Period for fast EMA
        slow (int): Period for slow EMA
        signal (int): Period for signal line smoothing

    Returns:
        dict: macd, signal, histogram (pd.Series)

    Example:
        - MACD > Signal: bullish momentum (buy)
        - MACD < Signal: bearish momentum (short)

        Fast EMA = 102, Slow EMA = 100 → MACD = 2
        Signal = EMA of MACD (say 1.8) → Histogram = 0.2
        MACD > Signal → bullish momentum (buy signal)

    🧠 Key Notes:

        Term	Meaning
        span=12	More sensitive to recent price action (short-term)
        span=26	Smoother, long-term trend
        adjust=False	Avoids initial bias, gives exponentially decayed weights
        ewm()	Exponential weighted moving average method in pandas
        
    """
    ema_fast = calculate_ema(df, fast)
    ema_slow = calculate_ema(df, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': macd_line - signal_line
    }
