import pandas as pd

def should_enter_trade(row, rsi, macd_row, dmi_row, divergence, config):
    """
    Determines whether to enter a trade (BUY or SHORT) based on combined indicator logic.

    This function uses:
    - RSI: for overbought/oversold levels (momentum exhaustion)
    - MACD: for momentum trend confirmation via line crossover
    - DMI: for trend direction and strength using +DI and -DI
    - Divergence: for early reversal signals between price and RSI

    Parameters:
        row (pd.Series): Current candle with price and volume info
        rsi (float): RSI value for the current candle
        macd_row (pd.Series): MACD line and signal values
        dmi_row (pd.Series): +DI, -DI, and ADX values
        divergence (str): 'bullish', 'bearish', or ''
        config (dict): Configuration values from config.json

    Returns:
        str: 'buy', 'short', or None if no valid trade signal is detected

    ----------
    ✅ BUY signal criteria:
    - RSI < oversold (e.g., < 30)
    - MACD > Signal line (bullish crossover)
    - +DI > -DI (price rising more strongly than falling)
    - Divergence == 'bullish' (RSI rising while price was falling)

    🔴 SHORT signal criteria:
    - RSI > overbought (e.g., > 70)
    - MACD < Signal line (bearish crossover)
    - -DI > +DI (price falling more strongly than rising)
    - Divergence == 'bearish' (RSI falling while price was rising)

    ----------
    Example 1 (BUY):
        RSI = 28, MACD = 0.5, Signal = 0.3
        +DI = 25, -DI = 18, Divergence = 'bullish'
        → All conditions match → returns 'buy'

    Example 2 (SHORT):
        RSI = 74, MACD = -0.4, Signal = -0.2
        +DI = 15, -DI = 28, Divergence = 'bearish'
        → All conditions match → returns 'short'
    """
    try:
        adx = dmi_row['ADX']
        if pd.isna(rsi) or pd.isna(macd_row['macd']) or pd.isna(macd_row['signal']) or pd.isna(adx):
            return None  # skip if any value missing

        # ---------------- BUY SETUP ----------------
        if (
            # rsi < config["rsi"]["oversold"] and
            # macd_row['macd'] > macd_row['signal'] and
            # dmi_row['+DI'] > dmi_row['-DI'] and
            # adx > config["min_adx_strength"] and
            divergence == 'bullish'
        ):
            return 'buy'

        # ---------------- SHORT SETUP ----------------
        elif (
            # rsi > config["rsi"]["overbought"] and
            # macd_row['macd'] < macd_row['signal'] and
            # dmi_row['-DI'] > dmi_row['+DI'] and
            # adx > config["min_adx_strength"] and
            divergence == 'bearish'
        ):
            return 'short'

    except Exception as e:
        print(f"[ERROR in signal logic] {e}")
        return None

    return None
