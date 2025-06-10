import pandas as pd

def calculate_dmi(df, period=14):
    """
    Calculates Directional Movement Index (DMI)
    Gives: +DI, -DI and ADX

    +DM = today's high - yesterday's high if it's greater than the drop
    -DM = yesterday's low - today's low if it's greater than the rise
    TR  = True Range (max of high-low, high-prev_close, low-prev_close)

    Parameters:
        df (pd.DataFrame): OHLC data
        period (int): Lookback window for smoothing

    Returns:
        dict of pd.Series: +DI, -DI, ADX

    Example:
        +DI > -DI and ADX > 20 → uptrend confirmed → trade allowed
        +DI < -DI → downtrend, potential short


    🧮 How DMI Works (Step-by-Step)

        1. Calculate True Range (TR):
            TR = max(
                current_high - current_low,
                abs(current_high - previous_close),
                abs(current_low - previous_close)
            )
        
        2. Calculate +DM and −DM (Directional Movements):
            +DM = current_high - previous_high  (only if it's greater than downward move and > 0)
            -DM = previous_low - current_low   (only if it's greater than upward move and > 0)
            Smooth TR, +DM, and −DM using Wilder’s method over a period (e.g., 14 candles).
        
        3. Calculate +DI and −DI:
            +DI = 100 * (Smoothed +DM / Smoothed TR)
            -DI = 100 * (Smoothed -DM / Smoothed TR)

        4. Calculate ADX (Trend Strength Indicator):
            DX = 100 * abs(+DI - -DI) / (+DI + -DI)
            ADX = EMA of DX over N periods (commonly 14)

    
    📊 Interpretation

        Scenario	Meaning
        +DI > −DI	Uptrend (Buy signal if other indicators agree)
        −DI > +DI	Downtrend (Short/Sell signal if others agree)
        ADX > 20–25	Trend is strong (regardless of direction)
        ADX < 20	Market is range-bound / sideways

    """

    # Step 1: Calculate change in highs and lows
    high_diff = df['high'].diff()
    low_diff = df['low'].diff()

    # Step 2: Compute +DM (upward movement) and -DM (downward movement)
    # +DM: only if high_diff > low_diff and it's positive
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0.0)

    # -DM: only if low_diff > high_diff and it's positive
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0.0)

    # Step 3: Calculate True Range (TR)
    tr1 = df['high'] - df['low']                          # High-Low range
    tr2 = (df['high'] - df['close'].shift()).abs()        # High - Prev Close
    tr3 = (df['low'] - df['close'].shift()).abs()         # Low - Prev Close

    # TR is the max of the three components above
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Smooth TR using rolling sum
    tr_sum = tr.rolling(window=period).sum()

    # Step 4: Calculate Directional Indicators
    # Smooth DM values
    plus_dm_sum = plus_dm.rolling(window=period).sum()
    minus_dm_sum = minus_dm.rolling(window=period).sum()

    # +DI and -DI as % of true range
    plus_di = 100 * (plus_dm_sum / (tr_sum + 1e-10))      # Avoid division by 0
    minus_di = 100 * (minus_dm_sum / (tr_sum + 1e-10))

    # Step 5: Calculate DX (Directional Index)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)) * 100

    # Step 6: Calculate ADX (Average DX) — measures trend **strength**
    adx = dx.rolling(window=period).mean()

    # Step 7: Return result as dictionary
    return {
        '+DI': plus_di,
        '-DI': minus_di,
        'ADX': adx
    }